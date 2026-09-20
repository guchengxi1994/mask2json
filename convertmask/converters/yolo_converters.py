"""YOLO txt -> VOC XML (needs origin images + a class file)."""

from __future__ import annotations

from pathlib import Path

from convertmask.converters.common import collect_files, collect_images, load_classes, pair_by_stem
from convertmask.core.annotation import Annotation
from convertmask.core.imageio import image_size
from convertmask.core.voc import write_voc

# class-table files that conventionally sit next to YOLO label txts and must
# not be treated as annotations when a directory is given
_CLASSFILE_BASENAMES = {"labels.txt", "classes.txt", "obj.names", "train.txt", "val.txt"}


def _collect_label_txts(txts: Path) -> list[Path]:
    files = collect_files(txts, {".txt"})
    return [p for p in files if p.name not in _CLASSFILE_BASENAMES]


def yolo_to_xml(
    txts: Path | str,
    imgs: Path | str,
    classes: Path | str,
    out: Path | str | None = None,
) -> list[Path]:
    """Convert YOLO txt file(s) into VOC XML.

    Boxes are denormalized with each image's own ``(width, height)``; files
    and images are paired by filename stem, for single files and
    directories alike (the legacy directory mode never worked). Files named
    ``labels.txt``/``classes.txt`` inside a directory are treated as class
    tables, not annotations.
    """
    if classes is None:
        raise ValueError("yolo2xml requires a class file (txt with one name per line)")
    class_map = load_classes(classes)
    names = list(class_map)

    txt_files = _collect_label_txts(Path(txts))
    if not txt_files:
        raise ValueError(f"no label .txt files in {txts}")
    pairs = pair_by_stem(txt_files, collect_images(imgs))
    out = Path(out) if out else txt_files[0].parent / "_xmls_"

    outputs = []
    for txt_path, img_path in pairs:
        width, height = image_size(img_path)
        lines = [
            line
            for line in txt_path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        ann = Annotation.from_yolo_lines(
            lines, names, width, height, image_path=Path(img_path).name
        )
        outputs.append(write_voc(ann, out / f"{img_path.stem}.xml"))
    return outputs
