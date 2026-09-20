"""Core augmentations: flip, rotation, translation, zoom, noise.

Noise types replace ``skimage.util.random_noise`` with plain numpy. All
geometric ops share one affine matrix between image and shapes, and masks
never go through interpolation (nearest only, in :mod:`compose`).
"""

from __future__ import annotations

import cv2
import numpy as np

from convertmask.augment.base import Augmentation, Variant, transform_shapes
from convertmask.core.annotation import Annotation

NOISE_TYPES = ("gaussian", "poisson", "s&p", "speckle")


class Flip(Augmentation):
    """Horizontal / vertical / both flips — three outputs (legacy behavior)."""

    name = "flip"

    @staticmethod
    def matrix(code: int, w: int, h: int) -> np.ndarray:
        m = np.eye(3)
        if code in (1, -1):  # horizontal: x' = w-1-x
            m = m @ np.array([[-1, 0, w - 1], [0, 1, 0], [0, 0, 1]])
        if code in (0, -1):  # vertical: y' = h-1-y
            m = m @ np.array([[1, 0, 0], [0, -1, h - 1], [0, 0, 1]])
        return m[:2]

    def variants(self, img, ann, rng):  # noqa: ARG002 (rng unused, deterministic)
        out: list[Variant] = []
        h, w = img.shape[:2]
        for code, tag in ((1, "h"), (0, "v"), (-1, "hv")):
            flipped = cv2.flip(img, code)
            shapes = []
            if ann is not None:
                shapes = transform_shapes(ann.shapes, self.matrix(code, w, h), w, h)
            out.append((flipped, _with_shapes(ann, shapes), tag))
        return out


class Rotation(Augmentation):
    """Canvas-preserving rotation; shapes mapped through the same matrix."""

    name = "rotation"

    def __init__(self, angle: float | None = None, scale: float = 1.0):
        self.angle = angle
        self.scale = scale

    def variants(self, img, ann, rng):
        angle = self.angle if self.angle is not None else float(rng.integers(-45, 46))
        h, w = img.shape[:2]
        m = cv2.getRotationMatrix2D((w / 2, h / 2), angle, self.scale)
        rotated = cv2.warpAffine(img, m, (w, h))
        shapes = transform_shapes(ann.shapes, m, w, h) if ann is not None else []
        tag = f"rot{int(angle)}" if angle == int(angle) else f"rot{angle:.1f}"
        return [(rotated, _with_shapes(ann, shapes), tag)]


class Translation(Augmentation):
    """Shift content; annotation points shift by the same offsets."""

    name = "translation"

    def __init__(self, th: int | None = None, tv: int | None = None,
                 factor: float = 0.2):
        self.th, self.tv, self.factor = th, tv, factor

    def variants(self, img, ann, rng):
        h, w = img.shape[:2]
        th = self.th if self.th is not None else int(rng.integers(-w // 5, w // 5 + 1))
        tv = self.tv if self.tv is not None else int(rng.integers(-h // 5, h // 5 + 1))
        m = np.float64([[1, 0, th], [0, 1, tv]])
        shifted = cv2.warpAffine(img, m, (w, h))
        shapes = transform_shapes(ann.shapes, m, w, h) if ann is not None else []
        return [(shifted, _with_shapes(ann, shapes), f"tr{th}_{tv}")]


class Zoom(Augmentation):
    """Scale about the center, cropping back to the original canvas.

    ``factor > 1`` zooms in (center crop), ``< 1`` zooms out (black border).
    """

    name = "zoom"

    def __init__(self, factor: float | None = None, lo: float = 0.8, hi: float = 1.8):
        self.factor, self.lo, self.hi = factor, lo, hi

    def variants(self, img, ann, rng):
        f = self.factor if self.factor is not None else round(
            float(rng.uniform(self.lo, self.hi)), 2
        )
        h, w = img.shape[:2]
        m = cv2.getRotationMatrix2D((w / 2, h / 2), 0, f)
        zoomed = cv2.warpAffine(img, m, (w, h))
        shapes = transform_shapes(ann.shapes, m, w, h) if ann is not None else []
        return [(zoomed, _with_shapes(ann, shapes), f"zoom{f}")]


class Noise(Augmentation):
    """Pixel noise (image only — geometry unchanged, so labels stay valid)."""

    name = "noise"

    def __init__(self, types: list[str] | None = None):
        self.types = list(types) if types else list(NOISE_TYPES)

    def variants(self, img, ann, rng):
        chosen = self.types or ["gaussian"]
        out = img
        for kind in chosen:
            out = add_noise(out, kind, rng)
        tag = "noise-" + "+".join(chosen)
        return [(out, ann, tag)]


def add_noise(img: np.ndarray, kind: str, rng: np.random.Generator) -> np.ndarray:
    data = img.astype(np.float64)
    if kind == "gaussian":
        noisy = data + rng.normal(0, 0.05 * 255, data.shape)
    elif kind == "s&p":
        noisy = data.copy()
        amount, salt_ratio = 0.02, 0.5
        mask = rng.random(data.shape[:2])
        noisy[mask < amount * salt_ratio] = 255  # salt
        noisy[mask > 1 - amount * (1 - salt_ratio)] = 0  # pepper
    elif kind == "speckle":
        noisy = data + data * rng.normal(0, 0.05, data.shape)
    elif kind == "poisson":
        noisy = rng.poisson(data / 255.0 * 30.0) / 30.0 * 255.0
    else:
        raise ValueError(f"unknown noise type {kind!r}; expected one of {NOISE_TYPES}")
    return np.clip(noisy, 0, 255).astype(np.uint8)


def _with_shapes(ann: Annotation | None, shapes: list) -> Annotation | None:
    if ann is None:
        return None
    new = Annotation(
        width=ann.width, height=ann.height, shapes=shapes,
        image_path=ann.image_path, label_names=ann.label_names,
    )
    return new
