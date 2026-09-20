"""labelme JSON -> mask images / VOC XML."""

from __future__ import annotations

import json
import logging
from pathlib import Path

import cv2
import numpy as np

from convertmask.converters.common import collect_files, load_classes
from convertmask.core.annotation import Annotation, Shape
from convertmask.core.b64 import decode_to_array
from convertmask.core.classfile import save_class_map
from convertmask.core.colormap import draw_label
from convertmask.core.imageio import write_image
from convertmask.core.labelmap import shapes_to_label
from convertmask.core.voc import write_voc

logger = logging.getLogger(__name__)

# legacy: objects smaller than 10 px per side are dropped in json->xml
MIN_SIZE_PX = 10


def _render_mask(
    ann: Annotation, classes: dict[str, int] | None
) -> tuple[np.ndarray, dict[str, int]]:
    """Return the class-value mask and the name->value map actually used."""
    if classes:
        used = {s.label: classes[s.label] for s in ann.shapes if s.label in classes}
        missing = sorted({s.label for s in ann.shapes if s.label not in classes})
        if missing:
            logger.warning("json2mask: classes not in class file, skipped: %s", missing)
        lbl = np.zeros((ann.height, ann.width), dtype=np.uint8)
        for s in ann.shapes:
            value = classes.get(s.label)
            if not value:
                continue
            poly = s.to_polygon().points
            if len(poly) < 2:
                continue
            pts = np.round(np.asarray(poly, dtype=np.float64)).astype(np.int64)
            cv2.fillPoly(lbl, [pts], int(value))
        return lbl, used

    lbl, names = shapes_to_label(ann.height, ann.width, ann.shapes)
    if len(names) == 2:  # single foreground class: legacy 0/255 output
        lbl = np.where(lbl > 0, 255, 0).astype(np.uint8)
        used = {names[1]: 255}
    else:
        used = {name: i for i, name in enumerate(names) if i > 0}
    return lbl, used


def json_to_mask(
    jsons: Path | str,
    out: Path | str | None = None,
    classes: Path | str | None = None,
) -> list[Path]:
    """Convert labelme JSON file(s) into mask images + visualization.

    Writes ``<out>/mask/<stem>.png``, ``<out>/mask_viz/<stem>_label_viz.png``,
    ``<out>/mask/label_names.txt`` and ``<out>/mask/info.yaml``.
    """
    class_map = load_classes(classes)
    files = collect_files(jsons, {".json"})
    if not files:
        raise ValueError(f"no .json files in {jsons}")
    out = Path(out) if out else (files[0].parent if len(files) == 1 else Path(jsons))
    mask_dir, viz_dir = out / "mask", out / "mask_viz"
    outputs: list[Path] = []
    name_value_map: dict[str, int] = {}

    for jf in files:
        ann = Annotation.load_labelme_json(jf)
        lbl, used = _render_mask(ann, class_map)
        name_value_map = used
        outputs.append(write_image(mask_dir / f"{jf.stem}.png", lbl))

        data = json.loads(jf.read_text(encoding="utf-8"))
        img = decode_to_array(data.get("imageData"))
        if img is None:
            img = np.zeros((ann.height, ann.width, 3), dtype=np.uint8)
        captions = ["_background_"] + [
            n for n, _ in sorted(used.items(), key=lambda kv: kv[1])
        ]
        viz = draw_label(lbl, img, captions)
        outputs.append(write_image(viz_dir / f"{jf.stem}_label_viz.png", viz))

    names = list(name_value_map)
    (mask_dir / "label_names.txt").write_text("\n".join(names) + "\n", encoding="utf-8")
    outputs.append(mask_dir / "label_names.txt")
    outputs.append(save_class_map(mask_dir / "info.yaml", name_value_map))
    return outputs


def json_to_xml(
    jsons: Path | str,
    out: Path | str | None = None,
) -> list[Path]:
    """Convert labelme JSON file(s) into VOC XML (bbox per shape)."""
    files = collect_files(jsons, {".json"})
    if not files:
        raise ValueError(f"no .json files in {jsons}")
    out = Path(out) if out else files[0].parent
    outputs = []
    for jf in files:
        ann = Annotation.load_labelme_json(jf)
        kept: list[Shape] = []
        for s in ann.shapes:
            xmin, ymin, xmax, ymax = s.bbox()
            # darknet-compatible: coordinates start at 1, not 0
            xmin, ymin = max(xmin, 1.0), max(ymin, 1.0)
            if (xmax - xmin) < MIN_SIZE_PX or (ymax - ymin) < MIN_SIZE_PX:
                logger.warning(
                    "json2xml: %s: object %r dropped (<%d px per side)",
                    jf.name, s.label, MIN_SIZE_PX,
                )
                continue
            kept.append(
                Shape(
                    label=s.label,
                    points=[[xmin, ymin], [xmax, ymin], [xmax, ymax], [xmin, ymax]],
                    difficult=s.difficult,
                )
            )
        ann.shapes = kept
        outputs.append(write_voc(ann, out / f"{jf.stem}.xml"))
    return outputs
