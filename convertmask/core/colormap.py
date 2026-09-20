"""Color maps and visualization rendering (replaces labelme's matplotlib-based helpers)."""

from __future__ import annotations

import cv2
import numpy as np


def label_colormap(n: int = 256) -> np.ndarray:
    """Return ``(n, 3)`` uint8 colors — the classic labelme bit-shuffle map."""
    cmap = np.zeros((n, 3), dtype=np.uint8)
    for i in range(n):
        c, r, g, b = i, 0, 0, 0
        for j in range(8):
            r |= ((c >> 0) & 1) << (7 - j)
            g |= ((c >> 1) & 1) << (7 - j)
            b |= ((c >> 2) & 1) << (7 - j)
            c >>= 3
        cmap[i] = [r, g, b]
    return cmap


def color_for(value: int) -> tuple[int, int, int]:
    colors = label_colormap(256)
    color = colors[int(value) % 256]
    return int(color[0]), int(color[1]), int(color[2])


def label2rgb(
    lbl: np.ndarray,
    img: np.ndarray | None = None,
    alpha: float = 0.5,
    thresh: float = 0.5,
) -> np.ndarray:
    """Blend a class-index map over an image (or over black).

    Semi-transparency follows pixel intensity like labelme: brighter source
    pixels get less overlay.
    """
    if lbl.ndim != 2:
        raise ValueError("label map must be 2-D")
    colors = label_colormap(256)
    rgb = colors[np.clip(lbl, 0, 255).astype(np.uint8)]
    if img is None:
        return rgb
    if img.ndim == 2:
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
    img = img.astype(np.float64)
    rgb = rgb.astype(np.float64)
    lum = img.astype(np.float64).mean(axis=2) / 255.0
    alpha_map = np.where(lum < thresh, alpha, alpha * 0.2)[..., None]
    out = rgb * alpha_map + img * (1 - alpha_map)
    return out.astype(np.uint8)


def draw_label(lbl: np.ndarray, img: np.ndarray | None, captions: list[str]) -> np.ndarray:
    """Render the labelme-style visualization: color overlay + caption strip.

    ``captions`` is indexed by label value; a horizontal legend strip is
    appended under the image with one color chip + text per class.
    """
    viz = label2rgb(lbl, img)

    # draw region boundaries
    if lbl.max() > 0:
        edges = (lbl > 0).astype(np.uint8) * 255
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cv2.polylines(viz, contours, True, (255, 255, 255), 1)

    chip_h = 22
    strip = np.full((chip_h * max(1, len(captions)), viz.shape[1], 3), 255, dtype=np.uint8)
    for i, caption in enumerate(captions):
        color = color_for(i)
        y0 = i * chip_h
        cv2.rectangle(strip, (0, y0), (chip_h, y0 + chip_h), color, -1)
        cv2.putText(
            strip,
            f"{i}: {caption}",
            (chip_h + 4, y0 + chip_h - 7),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 0, 0),
            1,
            cv2.LINE_AA,
        )
    return np.vstack([viz, strip])
