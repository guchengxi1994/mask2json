"""mask images -> labelme JSON (and mask -> VOC XML).

Class mapping: a txt/yaml class file maps mask pixel values to class names
(yaml values are used verbatim, txt assigns 1..N); without one, classes are
named ``class{value}`` from the mask's own pixel values.
"""

from __future__ import annotations

import logging
from pathlib import Path

import cv2
import numpy as np

from convertmask.converters.common import collect_images, load_classes, pair_by_stem
from convertmask.core.annotation import Annotation, Shape
from convertmask.core.b64 import encode_image
from convertmask.core.imageio import image_size, read_mask
from convertmask.core.voc import write_voc

logger = logging.getLogger(__name__)

# legacy defaults: drop specks below 20 px or under 10% of their bbox
MIN_AREA = 20.0
MIN_FILL = 0.1


def _mask_shapes(
    mask: np.ndarray, value_to_label: dict[int, str]
) -> list[Shape]:
    """Extract polygons per class value with legacy noise filtering."""
    shapes: list[Shape] = []
    for value, label in sorted(value_to_label.items()):
        binary = np.where(mask == value, 255, 0).astype(np.uint8)
        contours, _ = cv2.findContours(binary, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        for contour in contours:
            area = cv2.contourArea(contour)
            x, y, w, h = cv2.boundingRect(contour)
            if area < MIN_AREA or area < MIN_FILL * max(w * h, 1):
                continue
            eps = 0.002 * cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, eps, True)
            pts = [[float(p[0][0]), float(p[0][1])] for p in approx]
            if len(pts) >= 3:
                shapes.append(Shape(label=label, points=pts))
    return shapes


def _mask_boxes(mask: np.ndarray, value_to_label: dict[int, str]) -> list[Shape]:
    """Extract one bbox per connected component per class value."""
    shapes: list[Shape] = []
    for value, label in sorted(value_to_label.items()):
        binary = np.where(mask == value, 255, 0).astype(np.uint8)
        n, _, stats, _ = cv2.connectedComponentsWithStats(binary, connectivity=8)
        for i in range(1, n):  # 0 is background
            x, y, w, h, area = stats[i]
            if area < MIN_AREA:
                continue
            shapes.append(
                Shape(
                    label=label,
                    points=[[x, y], [x + w, y], [x + w, y + h], [x, y + h]],
                )
            )
    return shapes


def _class_values(mask: np.ndarray, classes: dict[str, int] | None) -> dict[int, str]:
    """Map the mask's pixel values to class names."""
    present = sorted(int(v) for v in np.unique(mask) if v > 0)
    if classes:
        id_to_name = {v: k for k, v in classes.items()}
        value_to_label = {v: id_to_name.get(v, f"class{v}") for v in present}
    else:
        value_to_label = {v: f"class{v}" for v in present}
    return value_to_label


def _prepare(imgs: Path | str, masks: Path | str) -> list[tuple[Path, Path]]:
    pairs = pair_by_stem(collect_images(imgs), collect_images(masks))
    if not pairs:
        raise ValueError(f"no image/mask pairs between {imgs} and {masks}")
    return pairs


def mask_to_json(
    imgs: Path | str,
    masks: Path | str,
    out: Path | str | None = None,
    classes: Path | str | None = None,
) -> list[Path]:
    """Convert mask images into labelme JSON files (one per image)."""
    class_map = load_classes(classes)
    out = Path(out) if out else Path(masks)
    outputs = []
    for img_path, mask_path in _prepare(imgs, masks):
        mask = read_mask(mask_path)
        width, height = image_size(img_path)
        if mask.shape != (height, width):
            raise ValueError(
                f"{mask_path.name}: mask shape {mask.shape[::-1]} != image {width}x{height}"
            )
        shapes = _mask_shapes(mask, _class_values(mask, class_map))
        if not shapes:
            logger.warning("mask_to_json: no shapes found in %s", mask_path)
        ann = Annotation(
            width=width,
            height=height,
            shapes=shapes,
            image_path=Path(img_path).name,
        )
        outputs.append(ann.save_labelme_json(out / f"{img_path.stem}.json",
                                             encode_image(img_path)))
    return outputs


def mask_to_xml(
    imgs: Path | str,
    masks: Path | str,
    out: Path | str | None = None,
    classes: Path | str | None = None,
) -> list[Path]:
    """Convert mask images into VOC XML files (bbox per component)."""
    class_map = load_classes(classes)
    out = Path(out) if out else Path(masks)
    outputs = []
    for img_path, mask_path in _prepare(imgs, masks):
        mask = read_mask(mask_path)
        width, height = image_size(img_path)
        if mask.shape != (height, width):
            raise ValueError(
                f"{mask_path.name}: mask shape {mask.shape[::-1]} != image {width}x{height}"
            )
        shapes = _mask_boxes(mask, _class_values(mask, class_map))
        ann = Annotation(
            width=width,
            height=height,
            shapes=shapes,
            image_path=Path(img_path).name,
        )
        outputs.append(write_voc(ann, out / f"{img_path.stem}.xml"))
    return outputs
