"""Augmentation pipeline: run methods in order, write image + annotation.

Each round applies the chosen methods to every branch the pipeline produces
(flip fans out to h/v/hv); the outputs of one stage feed the next. Every
augmented image is written together with a matching annotation file in the
input label format (labelme JSON or VOC XML), so results never appear
without their labels.
"""

from __future__ import annotations

import logging
from pathlib import Path

import numpy as np

from convertmask import AUG_METHODS, AUG_OPTIONAL_METHODS
from convertmask.augment.basic import Flip, Noise, Rotation, Translation, Zoom
from convertmask.augment.optional import (
    Crop,
    Cutmix,
    Distort,
    Inpaint,
    Mixup,
    Perspective,
    Resize,
)
from convertmask.core.annotation import Annotation
from convertmask.core.b64 import encode_image
from convertmask.core.imageio import read_image, write_image
from convertmask.core.labelmap import annotation_label_map
from convertmask.core.voc import read_voc, write_voc

logger = logging.getLogger(__name__)

_CORE = {
    "flip": Flip,
    "rotation": Rotation,
    "translation": Translation,
    "zoom": Zoom,
    "noise": Noise,
}

_OPTIONAL = {
    "crop": Crop,
    "inpaint": Inpaint,
    "perspective": Perspective,
    "resize": Resize,
    "distort": Distort,
}


def build(method: str, params: dict) -> object:
    """Instantiate an augmentation by name with CLI/API parameters."""
    if method in _CORE:
        return _CORE[method](**params)
    if method in _OPTIONAL:
        return _OPTIONAL[method](**params)
    if method in ("mixup", "cutmix"):
        other = params.pop("other", None)
        if other is None:
            raise ValueError(f"{method} needs an 'other' image (params['other'])")
        cls = Mixup if method == "mixup" else Cutmix
        return cls(other, params.get("factor", 0.5))
    raise ValueError(
        f"unknown augmentation {method!r}; core: {AUG_METHODS}, "
        f"optional: {AUG_OPTIONAL_METHODS}"
    )


def _load_annotation(label_path: Path) -> Annotation:
    if label_path.suffix == ".xml":
        return read_voc(label_path)
    return Annotation.load_labelme_json(label_path)


def augment_images(
    imgs: Path | str,
    labels: Path | str | None = None,
    methods: list[str] | None = None,
    number: int = 1,
    seed: int | None = None,
    out: Path | str | None = None,
    params: dict | None = None,
    label_fmt: str | None = None,
    save_mask: bool = False,
) -> list[Path]:
    """Augment images (optionally with annotations) and write results.

    ``methods`` defaults to the five core methods. ``labels`` points to
    labelme JSON or VOC XML files paired by stem; each output image is
    written with a matching annotation in the same format. ``label_fmt``
    ('json'|'xml'|'none') disambiguates mixed label dirs and forces
    unlabeled mode. Returns the list of written files.
    """
    from convertmask.converters.common import collect_files, collect_images, pair_by_stem

    params = params or {}
    methods = list(methods) if methods else list(AUG_METHODS)
    rng = np.random.default_rng(seed)

    image_files = collect_images(imgs)
    pairs: list[tuple[Path, Path | None]]
    if labels is None or label_fmt == "none":
        pairs = [(p, None) for p in image_files]
    else:
        label_files = collect_files(labels, {".json", ".xml"})
        suffixes = {p.suffix for p in label_files}
        if len(suffixes) == 2 and label_fmt is None:
            raise ValueError(
                f"{labels} mixes .json and .xml labels; pass label_fmt='json' or 'xml'"
            )
        if label_fmt in ("json", "xml"):
            label_files = [p for p in label_files if p.suffix == f".{label_fmt}"]
        pairs = pair_by_stem(image_files, label_files)
    if not pairs:
        raise ValueError(f"no images to augment in {imgs}")

    out = Path(out) if out else Path(imgs).parent / "augmented"
    out.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []

    for img_path, label_path in pairs:
        img = read_image(img_path)
        ann = _load_annotation(label_path) if label_path else None
        for round_no in range(number):
            # (image, annotation, method-chain tag)
            branches: list[tuple[np.ndarray, Annotation | None, str]] = [(img, ann, "")]
            for method in methods:
                stage = build(method, dict(params.get(method, {})))
                nxt: list[tuple[np.ndarray, Annotation | None, str]] = []
                for b_img, b_ann, b_tag in branches:
                    for v_img, v_ann, v_tag in stage.variants(b_img, b_ann, rng):
                        tag = f"{b_tag}-{v_tag}" if b_tag else v_tag
                        nxt.append((v_img, v_ann, tag))
                branches = nxt
            for b_img, b_ann, b_tag in branches:
                stem = f"{img_path.stem}_aug{round_no}_{b_tag}"
                written.append(write_image(out / f"{stem}.jpg", b_img))
                if b_ann is None:
                    continue
                b_ann.image_path = Path(f"{stem}.jpg")
                if label_path is not None and label_path.suffix == ".xml":
                    written.append(write_voc(b_ann, out / f"{stem}.xml"))
                else:
                    written.append(
                        b_ann.save_labelme_json(out / f"{stem}.json", encode_image(b_img))
                    )
                if save_mask:
                    mask, _ = annotation_label_map(b_ann)
                    written.append(write_image(out / "masks" / f"{stem}.png", mask))
    return written
