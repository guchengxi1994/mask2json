"""Pascal VOC XML reading/writing built on :mod:`xml.etree.ElementTree`.

The writer emits the same element layout the legacy tool produced
(``annotation > folder, filename, path, source>database, size, segmented,
object*``) except ``size/depth`` now reflects the real channel count.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path

from convertmask.core.annotation import Annotation, Shape


def _parse_int(text: str | None) -> int:
    if text is None:
        raise ValueError("missing integer element")
    return int(round(float(text.strip())))


def read_voc(path: Path, fallback_size: tuple[int, int] | None = None) -> Annotation:
    """Parse a VOC xml file into :class:`Annotation`.

    ``fallback_size`` (width, height) is used when the file's ``size``
    element is missing or zero — some generators (e.g. the legacy WIDER-face
    converter) wrote ``0x0``.
    """
    path = Path(path)
    root = ET.parse(path).getroot()

    size = root.find("size")
    if size is not None:
        width = _parse_int(size.findtext("width"))
        height = _parse_int(size.findtext("height"))
    else:
        width = height = 0
    if (width <= 0 or height <= 0) and fallback_size is not None:
        width, height = fallback_size
    if width <= 0 or height <= 0:
        raise ValueError(f"{path}: invalid or missing image size")

    filename = root.findtext("filename") or path.stem
    shapes = []
    for obj in root.findall("object"):
        name = (obj.findtext("name") or "").strip()
        difficult = _parse_int(obj.findtext("difficult") or "0") != 0
        bnd = obj.find("bndbox")
        if bnd is None:
            continue
        xmin = float(_parse_int(bnd.findtext("xmin")))
        ymin = float(_parse_int(bnd.findtext("ymin")))
        xmax = float(_parse_int(bnd.findtext("xmax")))
        ymax = float(_parse_int(bnd.findtext("ymax")))
        shapes.append(
            Shape(
                label=name,
                points=[[xmin, ymin], [xmax, ymin], [xmax, ymax], [xmin, ymax]],
                difficult=difficult,
            )
        )
    return Annotation(width=width, height=height, shapes=shapes,
                      image_path=Path(filename))


def write_voc(
    annotation: Annotation,
    path: Path,
    folder: str = "",
    depth: int = 3,
) -> Path:
    """Write ``annotation`` as a Pascal VOC xml file."""
    root = ET.Element("annotation")
    ET.SubElement(root, "folder").text = folder
    filename = annotation.image_path.name if annotation.image_path else Path(path).stem
    ET.SubElement(root, "filename").text = filename
    ET.SubElement(
        root, "path"
    ).text = str(annotation.image_path) if annotation.image_path else ""
    source = ET.SubElement(root, "source")
    ET.SubElement(source, "database").text = "Unknown"
    size = ET.SubElement(root, "size")
    ET.SubElement(size, "width").text = str(int(annotation.width))
    ET.SubElement(size, "height").text = str(int(annotation.height))
    ET.SubElement(size, "depth").text = str(int(depth))
    ET.SubElement(root, "segmented").text = "0"

    for shape in annotation.shapes:
        xmin, ymin, xmax, ymax = shape.bbox()
        obj = ET.SubElement(root, "object")
        ET.SubElement(obj, "name").text = shape.label
        ET.SubElement(obj, "difficult").text = "1" if shape.difficult else "0"
        bnd = ET.SubElement(obj, "bndbox")
        ET.SubElement(bnd, "xmin").text = str(int(round(xmin)))
        ET.SubElement(bnd, "ymin").text = str(int(round(ymin)))
        ET.SubElement(bnd, "xmax").text = str(int(round(xmax)))
        ET.SubElement(bnd, "ymax").text = str(int(round(ymax)))

    ET.indent(root, space="\t")
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    ET.ElementTree(root).write(path, encoding="utf-8", xml_declaration=True)
    return path
