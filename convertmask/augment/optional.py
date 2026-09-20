"""Optional augmentations.

- crop / inpaint / mixup / cutmix: image-only (geometry untouched or
  undefined for labels) — annotations are passed through unchanged.
- perspective / resize: geometric, shapes transform exactly with the image.
- distort: dense local warp; shapes are re-extracted from the warped label
  map so they follow the pixels (the legacy op ignored labels).
"""

from __future__ import annotations

import cv2
import numpy as np

from convertmask.augment.base import (
    Augmentation,
    resize_shapes,
    transform_shapes,
)
from convertmask.augment.basic import _with_shapes
from convertmask.core.labelmap import label_to_shapes, shapes_to_label


def _random_poly_mask(rng: np.random.Generator, h: int, w: int,
                      n_verts: int = 6) -> np.ndarray:
    cx, cy = rng.integers(w // 4, 3 * w // 4), rng.integers(h // 4, 3 * h // 4)
    radius = rng.integers(min(h, w) // 6, min(h, w) // 2)
    angles = np.sort(rng.uniform(0, 2 * np.pi, n_verts))
    xs = cx + radius * rng.uniform(0.5, 1.2, n_verts) * np.cos(angles)
    ys = cy + radius * rng.uniform(0.5, 1.2, n_verts) * np.sin(angles)
    mask = np.zeros((h, w), dtype=np.uint8)
    cv2.fillPoly(mask, [np.stack([xs, ys], axis=1).astype(np.int64)], 255)
    return mask


class Crop(Augmentation):
    """Erase (zero or noise-fill) a random rectangular or polygon region.

    Pixels change, geometry does not — annotations stay valid.
    """

    name = "crop"

    def __init__(self, rect: bool = True, number: int = 1, noise: bool = False):
        self.rect, self.number, self.noise = rect, number, noise

    def variants(self, img, ann, rng):
        out = img.copy()
        h, w = img.shape[:2]
        for _ in range(self.number):
            if self.rect:
                x0 = int(rng.integers(0, w // 2))
                y0 = int(rng.integers(0, h // 2))
                x1 = int(rng.integers(x0 + w // 4, w))
                y1 = int(rng.integers(y0 + h // 4, h))
                region = np.zeros((h, w), dtype=np.uint8)
                region[y0:y1, x0:x1] = 255
            else:
                region = _random_poly_mask(rng, h, w)
            if self.noise:
                fill = rng.integers(0, 256, out.shape, dtype=np.uint8)
                out[region > 0] = fill[region > 0]
            else:
                out[region > 0] = 0
        return [(out, ann, f"crop{self.number}")]


class Inpaint(Augmentation):
    """cv2 inpainting over a random region (image-only)."""

    name = "inpaint"

    def __init__(self, rect: bool = True):
        self.rect = rect

    def variants(self, img, ann, rng):
        h, w = img.shape[:2]
        if self.rect:
            x0 = int(rng.integers(0, w // 2))
            y0 = int(rng.integers(0, h // 2))
            region = np.zeros((h, w), dtype=np.uint8)
            region[y0 : y0 + h // 4, x0 : x0 + w // 4] = 255
        else:
            region = _random_poly_mask(rng, h, w)
        out = cv2.inpaint(img, region, 3, cv2.INPAINT_TELEA)
        return [(out, ann, "inpaint")]


class Perspective(Augmentation):
    """Random perspective warp with correct canvas size and corner order."""

    name = "perspective"

    def __init__(self, factor: float = 0.15):
        self.factor = factor

    def variants(self, img, ann, rng):
        h, w = img.shape[:2]
        f = self.factor
        # corner order TL, TR, BR, BL for BOTH point sets; both arrays must
        # stay float32 — getPerspectiveTransform rejects float64 input
        src = np.float32([[0, 0], [w - 1, 0], [w - 1, h - 1], [0, h - 1]])
        offsets = rng.uniform(0, f, (4, 2)) * np.array([[w, h]])
        dst = np.float32(src + offsets)
        m = cv2.getPerspectiveTransform(src, dst)
        warped = cv2.warpPerspective(img, m, (w, h))  # dsize is (width, height)
        shapes = transform_shapes(ann.shapes, np.asarray(m), w, h) if ann else []
        return [(warped, _with_shapes(ann, shapes), "perspective")]


class Resize(Augmentation):
    """Resize image and shape coordinates by independent factors."""

    name = "resize"

    def __init__(self, fx: float = 0.5, fy: float | None = None):
        self.fx, self.fy = fx, (fy if fy is not None else fx)

    def variants(self, img, ann, rng):  # noqa: ARG002
        h, w = img.shape[:2]
        new_w, new_h = max(1, int(round(w * self.fx))), max(1, int(round(h * self.fy)))
        out = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)
        shapes = resize_shapes(ann.shapes, new_w / w, new_h / h) if ann else []
        ann2 = _with_shapes(ann, shapes)
        if ann2 is not None:
            ann2.width, ann2.height = new_w, new_h
        return [(out, ann2, f"resize{new_w}x{new_h}")]


class Distort(Augmentation):
    """Local fisheye-style warp via a vectorized inverse map (cv2.remap).

    Shapes are rasterized per class, warped with the same map (nearest
    neighbor), and re-extracted — labels follow the pixels.
    """

    name = "distort"

    def __init__(self, radius_factor: float = 0.3, strength: float = 0.4):
        self.radius_factor, self.strength = radius_factor, strength

    def variants(self, img, ann, rng):
        h, w = img.shape[:2]
        center = np.array([rng.uniform(0.3, 0.7) * w, rng.uniform(0.3, 0.7) * h])
        # the warp is centered slightly off the visual center (mouse bias)
        focus = center + rng.uniform(-0.2, 0.2, 2) * np.array([w, h]) * 0.3
        radius = self.radius_factor * min(w, h)

        xs, ys = np.meshgrid(np.arange(w, dtype=np.float32),
                             np.arange(h, dtype=np.float32))
        dx, dy = xs - focus[0], ys - focus[1]
        dist = np.sqrt(dx**2 + dy**2)
        affected = (dist < radius) & (dist > 1e-6)
        scale = np.ones_like(dist)
        # fisheye: pixels inside the radius sample closer to the focus
        influence = (1 - dist / radius) ** 2 * self.strength
        scale[affected] -= influence[affected]
        map_x = (focus[0] + dx * scale).astype(np.float32)
        map_y = (focus[1] + dy * scale).astype(np.float32)
        out = cv2.remap(img, map_x, map_y, cv2.INTER_LINEAR)

        if ann is None or not ann.shapes:
            return [(out, ann, "distort")]

        lbl, names = shapes_to_label(h, w, ann.shapes)
        lbl_warped = cv2.remap(lbl, map_x, map_y, cv2.INTER_NEAREST)
        shapes = label_to_shapes(lbl_warped, names)
        return [(out, _with_shapes(ann, shapes), "distort")]


class Mixup(Augmentation):
    """Blend two images (unlabeled mode only)."""

    name = "mixup"

    def __init__(self, other: np.ndarray, factor: float = 0.5):
        self.other, self.factor = other, factor

    def variants(self, img, ann, rng):  # noqa: ARG002
        other = cv2.resize(self.other, (img.shape[1], img.shape[0]))
        out = cv2.addWeighted(img, self.factor, other, 1 - self.factor, 0)
        return [(out, ann, "mixup")]


class Cutmix(Augmentation):
    """Paste a random rect of another image (unlabeled mode only)."""

    name = "cutmix"

    def __init__(self, other: np.ndarray, factor: float = 0.4):
        self.other, self.factor = other, factor

    def variants(self, img, ann, rng):
        h, w = img.shape[:2]
        other = cv2.resize(self.other, (w, h))
        rw, rh = int(w * self.factor), int(h * self.factor)
        x0 = int(rng.integers(0, w - rw + 1))
        y0 = int(rng.integers(0, h - rh + 1))
        out = img.copy()
        out[y0 : y0 + rh, x0 : x0 + rw] = other[y0 : y0 + rh, x0 : x0 + rw]
        return [(out, ann, "cutmix")]
