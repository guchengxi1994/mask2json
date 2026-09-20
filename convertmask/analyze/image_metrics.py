"""Image-quality metrics: brightness, contrast, sharpness, noise, saturation."""

from __future__ import annotations

import cv2
import numpy as np


def image_metrics(img: np.ndarray) -> dict:
    """Compute quality metrics for an RGB image."""
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY) if img.ndim == 3 else img
    hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV) if img.ndim == 3 else None
    laplacian = cv2.Laplacian(gray, cv2.CV_64F)
    return {
        "brightness": round(float(gray.mean()), 2),
        "contrast": round(float(gray.std()), 2),
        "sharpness": round(float(laplacian.var()), 2),
        # Immerkaer's fast noise estimate: sigma = sqrt(pi/2) * mean|Laplacian|/6
        "noise": round(float(np.abs(laplacian).mean() * 0.855 / 6.0), 3),
        "saturation": round(float(hsv[..., 1].mean()), 2) if hsv is not None else None,
    }


def image_metrics_pathless(gray_or_rgb: np.ndarray) -> dict:
    return image_metrics(gray_or_rgb)


def metric_deltas(a: dict, b: dict) -> dict:
    """Differences (b - a) for shared numeric metrics, absolute and relative."""
    deltas = {}
    for k in a:
        if a[k] is None or b.get(k) is None:
            continue
        diff = round(float(b[k]) - float(a[k]), 3)
        rel = diff / float(a[k]) if a[k] != 0 else None
        deltas[k] = {
            "before": a[k],
            "after": b[k],
            "delta": diff,
            "ratio": round(rel, 3) if rel is not None else None,
        }
    return deltas


def histogram(gray: np.ndarray, bins: int = 32) -> list[int]:
    hist = cv2.calcHist([gray.astype(np.uint8)], [0], None, [bins], [0, 256])
    return [int(v) for v in hist.ravel()]
