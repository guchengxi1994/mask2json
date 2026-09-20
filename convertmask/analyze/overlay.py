"""Draw annotation overlays (boxes/polygons + labels) onto images."""

from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np

from convertmask.core.annotation import Annotation
from convertmask.core.colormap import color_for
from convertmask.core.imageio import read_image, write_image


def draw_overlay(
    img: np.ndarray,
    ann: Annotation,
    highlight: set[int] | None = None,
    line: int = 2,
) -> np.ndarray:
    """Return a copy of ``img`` with every shape drawn and labeled.

    ``highlight`` contains shape indices to outline in red (used by the
    analyzer to point at problematic objects).
    """
    canvas = img.copy()
    if canvas.ndim == 2:
        canvas = cv2.cvtColor(canvas, cv2.COLOR_GRAY2RGB)
    for i, s in enumerate(ann.shapes):
        color = (255, 0, 0) if (highlight and i in highlight) else color_for(
            (hash(s.label) % 200) + 3
        )
        pts = np.round(np.asarray(s.to_polygon().points)).astype(np.int64)
        cv2.polylines(canvas, [pts], True, color, line)
        xmin, ymin, xmax, ymax = s.bbox()
        cv2.putText(
            canvas, f"{i}:{s.label}", (int(xmin), max(10, int(ymin) - 4)),
            cv2.FONT_HERSHEY_SIMPLEX, 0.45, color, 1, cv2.LINE_AA,
        )
    return canvas


def save_overlay(
    img_path: Path, ann: Annotation, out_path: Path, highlight: set[int] | None = None
) -> Path:
    img = read_image(img_path)
    return write_image(out_path, draw_overlay(img, ann, highlight))
