"""VOC XML -> labelme JSON / YOLO txt / mask images."""

from __future__ import annotations

import logging
import xml.etree.ElementTree as ET
from pathlib import Path

import numpy as np

from convertmask.converters.common import collect_files, collect_images, load_classes, pair_by_stem
from convertmask.core.annotation import Annotation, Shape
from convertmask.core.b64 import encode_image
from convertmask.core.classfile import save_class_map
from convertmask.core.imageio import image_size, write_image
from convertmask.core.voc import read_voc

logger = logging.getLogger(__name__)


# --------------------------------------------------------------------- #
# xml -> json


def _parse_polygon_xml(xml_path: Path) -> list[Shape]:
    """Parse LabelImgTool-style ``<polygon><point0>x,y</point0>`` objects."""
    root = ET.parse(xml_path).getroot()
    shapes = []
    for obj in root.findall("object"):
        polygon = obj.find("polygon")
        if polygon is None:
            continue
        name = (obj.findtext("name") or "").strip()
        points = []
        for child in polygon:  # point0, point1, ... in document order
            text = (child.text or "").strip().strip("[]()")
            if "," not in text:
                continue
            x_s, y_s = text.split(",", 1)
            points.append([float(x_s), float(y_s)])
        if len(points) > 2:
            shapes.append(Shape(label=name, points=points))
    return shapes


def xml_to_json(
    xmls: Path | str,
    imgs: Path | str,
    out: Path | str | None = None,
) -> list[Path]:
    """Convert VOC/LabeledXml files into labelme JSON.

    Objects carrying a ``<polygon>`` element are read as polygons
    (LabelImgTool convention); plain ``bndbox`` objects become 4-corner
    polygons (legacy ``x2jConvert_pascal`` behavior).
    """
    xml_files = collect_files(xmls, {".xml"})
    if not xml_files:
        raise ValueError(f"no .xml files in {xmls}")
    pairs = pair_by_stem(xml_files, collect_images(imgs))
    out = Path(out) if out else pairs[0][0].parent
    outputs = []
    for xml_path, img_path in pairs:
        width, height = image_size(img_path)
        polygon_shapes = _parse_polygon_xml(xml_path)
        if polygon_shapes:
            shapes = polygon_shapes
        else:
            ann = read_voc(xml_path, fallback_size=(width, height))
            shapes = [s.to_polygon() for s in ann.shapes]
        ann = Annotation(
            width=width, height=height, shapes=shapes, image_path=Path(img_path).name
        )
        outputs.append(
            ann.save_labelme_json(out / f"{img_path.stem}.json", encode_image(img_path))
        )
    return outputs


# --------------------------------------------------------------------- #
# xml -> yolo


def xml_to_yolo(
    xmls: Path | str,
    out: Path | str | None = None,
    classes: Path | str | None = None,
) -> list[Path]:
    """Convert VOC XML file(s) into YOLO txt files.

    The class table is fixed up front — from the class file when given,
    otherwise accumulated over *all* input files — so every output uses the
    same ids (the legacy tool reset the table between files). ``labels.txt``
    is written alongside the outputs.
    """
    xml_files = collect_files(xmls, {".xml"})
    if not xml_files:
        raise ValueError(f"no .xml files in {xmls}")
    out = Path(out) if out else (
        xml_files[0].parent if len(xml_files) == 1 else xml_files[0].parent
    )

    annotations = []
    for xml_path in xml_files:
        ann = read_voc(xml_path)
        annotations.append((xml_path, ann))

    if classes:
        class_map = load_classes(classes)
        names = list(class_map)
    else:
        names = []
        for _, ann in annotations:
            for s in ann.shapes:
                if s.label and s.label not in names:
                    names.append(s.label)
    label_names = ["_background_", *names]

    outputs = []
    for xml_path, ann in annotations:
        ann.label_names = label_names
        lines, _ = ann.to_yolo_lines()
        unknown = [
            s.label for s in ann.shapes
            if s.label and s.label not in names
        ]
        if unknown:
            logger.warning(
                "xml2yolo: %s: labels not in class file written as id -1: %s",
                xml_path.name, sorted(set(unknown)),
            )
        txt_path = out / f"{xml_path.stem}.txt"
        txt_path.parent.mkdir(parents=True, exist_ok=True)
        txt_path.write_text("".join(line + "\n" for line in lines), encoding="utf-8")
        outputs.append(txt_path)

    labels_path = out / "labels.txt"
    labels_path.write_text("\n".join(names) + "\n", encoding="utf-8")
    outputs.append(labels_path)
    return outputs


# --------------------------------------------------------------------- #
# xml -> mask


def xml_to_mask(
    xmls: Path | str,
    out: Path | str | None = None,
    classes: Path | str | None = None,
) -> list[Path]:
    """Convert VOC XML file(s) into class-id mask images (PNG, lossless).

    Mask values come from the class file (yaml values verbatim, txt 1..N);
    without one, ids follow first appearance across all files.
    """
    xml_files = collect_files(xmls, {".xml"})
    if not xml_files:
        raise ValueError(f"no .xml files in {xmls}")
    out = Path(out) if out else xml_files[0].parent
    mask_dir = out / "mask"

    parsed = [(p, read_voc(p)) for p in xml_files]

    if classes:
        class_map = load_classes(classes)
    else:
        class_map = {}
        for _, ann in parsed:
            for s in ann.shapes:
                if s.label and s.label not in class_map:
                    class_map[s.label] = len(class_map) + 1

    outputs = []
    for xml_path, ann in parsed:
        mask = np.zeros((ann.height, ann.width), dtype=np.uint8)
        for s in ann.shapes:
            value = class_map.get(s.label)
            if not value:
                logger.warning("xml2mask: unknown class %r skipped", s.label)
                continue
            xmin, ymin, xmax, ymax = (int(round(v)) for v in s.bbox())
            mask[ymin:ymax, xmin:xmax] = int(value)
        outputs.append(write_image(mask_dir / f"{xml_path.stem}.png", mask))

    outputs.append(save_class_map(mask_dir / "info.yaml", class_map))
    (mask_dir / "label_names.txt").write_text(
        "\n".join(class_map) + "\n", encoding="utf-8"
    )
    outputs.append(mask_dir / "label_names.txt")
    return outputs
