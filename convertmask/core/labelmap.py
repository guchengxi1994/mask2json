"""Rasterize shapes into class-index label maps and back.

Replaces ``labelme.utils.shapes_to_label``: ids are assigned 1..N in
first-appearance order of shape labels, 0 is background — matching the
legacy tool's mask convention when no explicit class file is given.
"""

from __future__ import annotations

import cv2
import numpy as np

from convertmask.core.annotation import BACKGROUND, Annotation, Shape


def shapes_to_label(height: int, width: int, shapes: list[Shape]) -> tuple[np.ndarray, list[str]]:
    """Rasterize shapes into ``(label_map, label_names)``.

    ``label_map`` is ``uint8`` with value ``i`` where ``label_names[i]`` is
    the class of the topmost shape covering the pixel; ``label_names[0]`` is
    always ``_background_``. Later shapes overwrite earlier ones where they
    overlap (labelme behavior).
    """
    labels = [BACKGROUND]
    for s in shapes:
        if s.label not in labels:
            labels.append(s.label)
    lbl = np.zeros((height, width), dtype=np.uint8)
    for s in shapes:
        value = labels.index(s.label)
        poly = s.to_polygon().points
        if len(poly) < 2:
            continue
        pts = np.round(np.asarray(poly, dtype=np.float64)).astype(np.int64)
        cv2.fillPoly(lbl, [pts], value)
    return lbl, labels


def label_to_shapes(label_map: np.ndarray, label_names: list[str]) -> list[Shape]:
    """Inflate a label map back to shapes — one polygon per class value.

    This is the inverse used when only a mask is at hand; contours are
    extracted with ``findContours`` + ``approxPolyDP``.
    """
    shapes: list[Shape] = []
    if label_map.size == 0:
        return shapes
    for value in range(1, int(label_map.max()) + 1):
        if (label_map == value).sum() == 0:
            continue
        label = label_names[value] if value < len(label_names) else f"class{value}"
        binary = np.where(label_map == value, 255, 0).astype(np.uint8)
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for contour in contours:
            if cv2.contourArea(contour) < 1.0:
                continue
            eps = 0.002 * cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, eps, True)
            pts = [[float(p[0][0]), float(p[0][1])] for p in approx]
            if len(pts) >= 3:
                shapes.append(Shape(label=label, points=pts))
    return shapes


def annotation_label_map(annotation: Annotation) -> tuple[np.ndarray, list[str]]:
    """Rasterize an annotation's shapes (ids from its class table)."""
    names = [BACKGROUND, *annotation.class_table()]
    lbl = np.zeros((annotation.height, annotation.width), dtype=np.uint8)
    for s in annotation.shapes:
        if s.label not in names:
            continue
        value = names.index(s.label)
        poly = s.to_polygon().points
        if len(poly) < 2:
            continue
        pts = np.round(np.asarray(poly, dtype=np.float64)).astype(np.int64)
        cv2.fillPoly(lbl, [pts], value)
    return lbl, names
