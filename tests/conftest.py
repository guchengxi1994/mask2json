"""Shared fixtures: tiny synthetic images and annotation builders."""

from __future__ import annotations

import numpy as np
import pytest

from convertmask.core.annotation import Annotation, Shape


def make_image(width: int = 120, height: int = 80) -> np.ndarray:
    """Non-square RGB test image (catches width/height axis swaps)."""
    rng = np.random.default_rng(0)
    return rng.integers(0, 255, size=(height, width, 3), dtype=np.uint8)


def make_mask(width: int = 120, height: int = 80) -> np.ndarray:
    """Two-class mask: rectangle of class 1 on the left, class 2 on the right."""
    mask = np.zeros((height, width), dtype=np.uint8)
    mask[10:40, 5:50] = 1
    mask[20:60, 60:110] = 2
    return mask


@pytest.fixture
def rgb_image() -> np.ndarray:
    return make_image()


@pytest.fixture
def class_mask() -> np.ndarray:
    return make_mask()


@pytest.fixture
def annotation() -> Annotation:
    """Annotation matching :func:`make_mask` bounding boxes."""
    return Annotation(
        width=120,
        height=80,
        shapes=[
            Shape(label="cat", points=[[5, 10], [50, 10], [50, 40], [5, 40]]),
            Shape(label="dog", points=[[60, 20], [110, 20], [110, 60], [60, 60]]),
        ],
    )
