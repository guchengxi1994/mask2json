"""Augmentation base: image and annotation must transform together.

Every augmentation takes ``(img, ann)`` and returns a list of
``(img, ann, tag)`` variants (most return one; flip returns three).
Geometric ops map polygon/bbox points through the exact same transform as
the pixels — the legacy tool's bbox drift (edge-midpoint AABBs, unclamped
boxes) cannot recur by construction.
"""

from __future__ import annotations

import numpy as np

from convertmask.core.annotation import Annotation, Shape

Variant = tuple[np.ndarray, Annotation | None, str]


class Augmentation:
    """Base class. Subclasses implement :meth:`variants`."""

    name = "aug"

    def variants(
        self, img: np.ndarray, ann: Annotation | None, rng: np.random.Generator
    ) -> list[Variant]:
        raise NotImplementedError


# --------------------------------------------------------------------- #
# geometry helpers


def transform_points(points: np.ndarray, matrix: np.ndarray) -> np.ndarray:
    """Apply a 2x3 (or 3x3) homography to ``(N, 2)`` points."""
    pts = np.hstack([points.astype(np.float64), np.ones((len(points), 1))])
    m = matrix if matrix.shape == (3, 3) else np.vstack([matrix, [0, 0, 1]])
    out = pts @ m.T
    return out[:, :2] / out[:, 2:3]


def clip_polygon(points: np.ndarray, width: int, height: int) -> np.ndarray | None:
    """Sutherland-Hodgman clip against the image rectangle.

    Inside test per bound is ``normal @ p + offset >= 0``:
    ``(1,0,0)`` -> x >= 0, ``(-1,0,w-1)`` -> x <= w-1, etc.
    """
    bounds = [
        (np.array([1.0, 0.0]), 0.0),           # x >= 0
        (np.array([-1.0, 0.0]), float(width - 1)),  # x <= w-1
        (np.array([0.0, 1.0]), 0.0),           # y >= 0
        (np.array([0.0, -1.0]), float(height - 1)),  # y <= h-1
    ]
    poly = points.astype(np.float64)
    for normal, offset in bounds:
        if len(poly) == 0:
            return None
        inside = poly @ normal + offset >= 0
        new_poly = []
        for i in range(len(poly)):
            cur, nxt = poly[i], poly[(i + 1) % len(poly)]
            cur_in, nxt_in = bool(inside[i]), bool(inside[(i + 1) % len(poly)])
            if cur_in:
                new_poly.append(cur)
            if cur_in != nxt_in:
                edge = nxt - cur
                denom = normal @ edge
                if abs(denom) > 1e-12:
                    t = -(normal @ cur + offset) / denom
                    new_poly.append(cur + t * edge)
        poly = np.asarray(new_poly)
    if len(poly) < 3:
        return None
    return poly


MIN_BOX_SIDE = 2.0  # px; boxes smaller than this are dropped


def transform_shapes(
    shapes: list[Shape],
    matrix: np.ndarray,
    width: int,
    height: int,
    clip: bool = True,
) -> list[Shape]:
    """Map every shape's points through ``matrix`` and clip to the canvas.

    Shapes whose clipped region degenerates or falls fully outside are
    dropped — silently writing out-of-frame boxes (legacy behavior) is not
    allowed. Pass ``clip=False`` for pure scaling (resize).
    """
    out: list[Shape] = []
    for s in shapes:
        pts = np.asarray(s.to_polygon().points, dtype=np.float64)
        moved = transform_points(pts, matrix)
        if clip:
            moved = clip_polygon(moved, width, height)
            if moved is None:
                continue
        xmin, ymin = moved.min(axis=0)
        xmax, ymax = moved.max(axis=0)
        if (xmax - xmin) < MIN_BOX_SIDE or (ymax - ymin) < MIN_BOX_SIDE:
            continue
        out.append(
            Shape(
                label=s.label,
                points=[[float(x), float(y)] for x, y in moved],
                group_id=s.group_id,
                flags=dict(s.flags),
                difficult=s.difficult,
            )
        )
    return out


def resize_shapes(shapes: list[Shape], fx: float, fy: float) -> list[Shape]:
    """Scale shape coordinates by independent x/y factors (resize op)."""
    return transform_shapes(
        shapes, np.array([[fx, 0, 0], [0, fy, 0]]), 0, 0, clip=False
    )
