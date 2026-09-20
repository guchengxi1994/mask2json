"""Converter tests: round-trips must be lossless, legacy bugs must stay fixed."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from convertmask.converters import convert, normalize_method
from tests.conftest import make_image, make_mask

STATIC = Path(__file__).resolve().parent.parent / "static"


def write_files(tmp_path: Path, files: dict[str, object]) -> Path:
    for name, content in files.items():
        p = tmp_path / name
        p.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(content, bytes):
            p.write_bytes(content)
        else:
            p.write_text(str(content), encoding="utf-8")
    return tmp_path


# --------------------------------------------------------------------- #
# mask -> json -> mask


def test_mask2json_round_trip(tmp_path):
    import cv2

    imgs, masks = tmp_path / "imgs", tmp_path / "masks"
    imgs.mkdir(), masks.mkdir()
    write_image_rgb = make_image()
    cv2.imwrite(str(imgs / "a.jpg"), write_image_rgb[..., ::-1])
    cv2.imwrite(str(masks / "a.png"), make_mask())

    jsons = convert("mask2json", imgs=imgs, masks=masks, out=tmp_path / "out")
    assert len(jsons) == 1
    data = json.loads(jsons[0].read_text(encoding="utf-8"))
    assert data["imageWidth"] == 120 and data["imageHeight"] == 80
    labels = {s["label"] for s in data["shapes"]}
    assert labels == {"class1", "class2"}

    outs = convert("json2mask", jsons=jsons[0], out=tmp_path / "out")
    mask_back = read_mask_png(tmp_path / "out" / "mask" / "a.png")
    orig = make_mask()
    # class1/class2 were auto-named from values 1/2 -> ids by appearance
    for value in (1, 2):
        inter = ((orig == value) & (mask_back == value)).sum()
        union = ((orig == value) | (mask_back == value)).sum()
        assert inter / union > 0.9, f"class {value} region lost"
    assert (tmp_path / "out" / "mask" / "info.yaml").exists()
    assert (tmp_path / "out" / "mask_viz" / "a_label_viz.png").exists()
    assert outs


def read_mask_png(path: Path) -> np.ndarray:
    import cv2

    return cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)


def test_mask2json_with_classfile(tmp_path):
    import cv2

    imgs, masks = tmp_path / "imgs", tmp_path / "masks"
    imgs.mkdir(), masks.mkdir()
    cv2.imwrite(str(imgs / "a.jpg"), make_image()[..., ::-1])
    cv2.imwrite(str(masks / "a.png"), make_mask())
    (tmp_path / "classes.txt").write_text("cat\ndog\n", encoding="utf-8")

    jsons = convert(
        "m2j", imgs=imgs, masks=masks, classes=tmp_path / "classes.txt"
    )  # alias also works
    data = json.loads(jsons[0].read_text(encoding="utf-8"))
    assert {s["label"] for s in data["shapes"]} == {"cat", "dog"}


def test_mask2json_speck_filtered(tmp_path):
    import cv2

    imgs, masks = tmp_path / "imgs", tmp_path / "masks"
    imgs.mkdir(), masks.mkdir()
    cv2.imwrite(str(imgs / "a.jpg"), make_image()[..., ::-1])
    mask = make_mask()
    mask[70:73, 70:73] = 1  # 3x3 speck below MIN_AREA
    cv2.imwrite(str(masks / "a.png"), mask)
    jsons = convert("mask2json", imgs=imgs, masks=masks)
    data = json.loads(jsons[0].read_text(encoding="utf-8"))
    boxes = [s["points"] for s in data["shapes"]]
    assert len(boxes) == 2  # speck dropped


def test_mask2json_size_mismatch_raises(tmp_path):
    import cv2

    imgs, masks = tmp_path / "imgs", tmp_path / "masks"
    imgs.mkdir(), masks.mkdir()
    cv2.imwrite(str(imgs / "a.jpg"), make_image()[..., ::-1])
    cv2.imwrite(str(masks / "a.png"), make_mask()[:40])  # wrong height
    with pytest.raises(ValueError, match="mask shape"):
        convert("mask2json", imgs=imgs, masks=masks)


def test_mask2xml(tmp_path):
    import cv2

    imgs, masks = tmp_path / "imgs", tmp_path / "masks"
    imgs.mkdir(), masks.mkdir()
    cv2.imwrite(str(imgs / "a.jpg"), make_image()[..., ::-1])
    cv2.imwrite(str(masks / "a.png"), make_mask())
    xmls = convert("mask2xml", imgs=imgs, masks=masks)
    from convertmask.core.voc import read_voc

    ann = read_voc(xmls[0])
    boxes = sorted(s.bbox() for s in ann.shapes)
    assert (5, 10, 50, 40) in boxes
    assert (60, 20, 110, 60) in boxes


# --------------------------------------------------------------------- #
# xml <-> yolo round trip (axis regression)


@pytest.fixture
def yolo_env(tmp_path):
    import cv2

    from convertmask.core.annotation import Annotation, Shape
    from convertmask.core.voc import write_voc

    ann1 = Annotation(
        width=120, height=80,
        image_path=Path("a.jpg"),
        shapes=[Shape("cat", [[5, 10], [50, 10], [50, 40], [5, 40]])],
    )
    ann2 = Annotation(
        width=120, height=80,
        image_path=Path("b.jpg"),
        shapes=[Shape("dog", [[60, 20], [110, 20], [110, 60], [60, 60]])],
    )
    xml_dir, img_dir = tmp_path / "xmls", tmp_path / "imgs"
    xml_dir.mkdir(), img_dir.mkdir()
    write_voc(ann1, xml_dir / "a.xml")
    write_voc(ann2, xml_dir / "b.xml")
    cv2.imwrite(str(img_dir / "a.jpg"), make_image()[..., ::-1])
    cv2.imwrite(str(img_dir / "b.jpg"), make_image()[..., ::-1])
    (tmp_path / "classes.txt").write_text("cat\ndog\n", encoding="utf-8")
    return tmp_path


def test_xml2yolo_yolo2xml_round_trip(yolo_env, tmp_path_factory):
    out = tmp_path_factory.mktemp("roundtrip")
    txts = convert("xml2yolo", xmls=yolo_env / "xmls", out=out)
    labels = [p for p in txts if p.name == "labels.txt"][0]
    names = labels.read_text(encoding="utf-8").split()
    assert names == ["cat", "dog"]

    xmls = convert(
        "yolo2xml",
        txts=out,
        imgs=yolo_env / "imgs",
        classes=yolo_env / "classes.txt",
    )
    from convertmask.core.voc import read_voc

    ann1 = read_voc([p for p in xmls if p.stem == "a"][0])
    ann2 = read_voc([p for p in xmls if p.stem == "b"][0])
    xmin, ymin, xmax, ymax = ann1.shapes[0].bbox()
    assert (xmin, ymin, xmax, ymax) == (5, 10, 50, 40)
    xmin, ymin, xmax, ymax = ann2.shapes[0].bbox()
    assert (xmin, ymin, xmax, ymax) == (60, 20, 110, 60)


def test_xml2yolo_class_ids_stable_across_files(yolo_env, tmp_path_factory):
    """Regression: legacy reset the class table between files."""
    out = tmp_path_factory.mktemp("stable")
    txts = convert("xml2yolo", xmls=yolo_env / "xmls", out=out)
    a = [p for p in txts if p.name == "a.txt"][0].read_text().splitlines()
    b = [p for p in txts if p.name == "b.txt"][0].read_text().splitlines()
    assert a[0].split()[0] == "0"  # cat = 0 everywhere
    assert b[0].split()[0] == "1"  # dog = 1 everywhere


def test_yolo2xml_directory_mode(yolo_env, tmp_path_factory):
    """Regression: legacy directory mode always failed with 'image not found'."""
    out = tmp_path_factory.mktemp("y2x")
    txts_dir = tmp_path_factory.mktemp("txts")
    convert("xml2yolo", xmls=yolo_env / "xmls", out=txts_dir)
    txt_inputs = [p for p in txts_dir.iterdir() if p.suffix == ".txt"]
    assert len(txt_inputs) == 3  # a.txt, b.txt + labels.txt (a class table)
    xmls = convert(
        "yolo2xml", txts=txts_dir, imgs=yolo_env / "imgs",
        classes=yolo_env / "classes.txt", out=out,
    )
    assert len(xmls) == 2


# --------------------------------------------------------------------- #
# json <-> xml


def test_json2xml_xml2json_round_trip(tmp_path):
    from convertmask.core.annotation import Annotation, Shape
    from convertmask.core.voc import read_voc

    ann = Annotation(
        width=120, height=80, image_path=Path("a.jpg"),
        shapes=[
            Shape("cat", [[5, 10], [50, 10], [50, 40], [5, 40]]),
            Shape("dog", [[60, 20], [110, 20], [110, 60], [60, 60]]),
        ],
    )
    jf = ann.save_labelme_json(tmp_path / "a.json", "QUJD")
    xmls = convert("json2xml", jsons=jf)
    ann2 = read_voc(xmls[0])
    assert [s.bbox() for s in ann2.shapes] == [(5, 10, 50, 40), (60, 20, 110, 60)]

    import cv2

    img_dir = tmp_path / "imgs"
    img_dir.mkdir()
    cv2.imwrite(str(img_dir / "a.jpg"), make_image()[..., ::-1])
    jsons = convert("xml2json", xmls=xmls[0], imgs=img_dir)
    data = json.loads(jsons[0].read_text(encoding="utf-8"))
    assert data["imageWidth"] == 120 and data["imageHeight"] == 80
    assert {s["label"] for s in data["shapes"]} == {"cat", "dog"}
    for s in data["shapes"]:
        xs = [p[0] for p in s["points"]]
        ys = [p[1] for p in s["points"]]
        assert (min(xs), min(ys), max(xs), max(ys)) in {(5, 10, 50, 40), (60, 20, 110, 60)}


def test_json2xml_drops_small_and_clamps_zero(tmp_path):
    from convertmask.core.annotation import Annotation, Shape

    ann = Annotation(
        width=120, height=80, image_path=Path("a.jpg"),
        shapes=[
            Shape("tiny", [[0, 0], [3, 0], [3, 3], [0, 3]]),  # dropped
            Shape("edge", [[0, 5], [40, 5], [40, 45], [0, 45]]),  # xmin clamped to 1
        ],
    )
    jf = ann.save_labelme_json(tmp_path / "a.json")
    xmls = convert("json2xml", jsons=jf)
    from convertmask.core.voc import read_voc

    ann2 = read_voc(xmls[0])
    assert [s.label for s in ann2.shapes] == ["edge"]
    assert ann2.shapes[0].bbox() == (1, 5, 40, 45)


def test_json2mask_yaml_values(tmp_path):
    from convertmask.core.annotation import Annotation, Shape

    ann = Annotation(
        width=120, height=80, image_path=Path("a.jpg"),
        shapes=[
            Shape("cat", [[5, 10], [50, 10], [50, 40], [5, 40]]),
            Shape("dog", [[60, 20], [110, 20], [110, 60], [60, 60]]),
        ],
    )
    jf = ann.save_labelme_json(tmp_path / "a.json")
    (tmp_path / "info.yaml").write_text(
        "label_names:\n  _background_: 0\n  cat: 1\n  dog: 255\n", encoding="utf-8"
    )
    convert("json2mask", jsons=jf, classes=tmp_path / "info.yaml", out=tmp_path)
    mask = read_mask_png(tmp_path / "mask" / "a.png")
    assert mask[20, 20] == 1
    assert mask[40, 80] == 255


def test_json2mask_single_class_binary255(tmp_path):
    from convertmask.core.annotation import Annotation, Shape

    ann = Annotation(
        width=60, height=60, image_path=Path("a.jpg"),
        shapes=[Shape("cat", [[5, 10], [50, 10], [50, 40], [5, 40]])],
    )
    jf = ann.save_labelme_json(tmp_path / "a.json")
    convert("json2mask", jsons=jf, out=tmp_path)
    mask = read_mask_png(tmp_path / "mask" / "a.png")
    assert set(np.unique(mask)) == {0, 255}  # legacy single-class convention


# --------------------------------------------------------------------- #
# xml2mask


def test_xml2mask_values_and_lossless(tmp_path):
    from convertmask.core.annotation import Annotation, Shape
    from convertmask.core.voc import write_voc

    ann = Annotation(
        width=120, height=80, image_path=Path("a.jpg"),
        shapes=[
            Shape("cat", [[5, 10], [50, 10], [50, 40], [5, 40]]),
            Shape("dog", [[60, 20], [110, 20], [110, 60], [60, 60]]),
        ],
    )
    write_voc(ann, tmp_path / "a.xml")
    outs = convert("xml2mask", xmls=tmp_path / "a.xml", out=tmp_path)
    mask = read_mask_png(tmp_path / "mask" / "a.png")
    assert mask[20, 20] == 1 and mask[40, 80] == 2
    assert Path(tmp_path / "mask" / "info.yaml").exists()
    assert outs


# --------------------------------------------------------------------- #
# dispatch


def test_dispatch_alias_and_errors():
    assert normalize_method("m2j") == "mask2json"
    with pytest.raises(ValueError, match="unknown method"):
        normalize_method("nope")
    with pytest.raises(TypeError, match="unexpected"):
        convert("json2xml", jsons="x", classes="y")


# --------------------------------------------------------------------- #
# golden fixtures from static/


@pytest.mark.skipif(not (STATIC / "multi_objs.xml").exists(), reason="fixture missing")
def test_golden_parse_multi_objs():
    from convertmask.core.voc import read_voc

    ann = read_voc(STATIC / "multi_objs.xml")
    assert (ann.width, ann.height) == (500, 482)
    assert sorted({s.label for s in ann.shapes}) == ["fruit1", "fruit2", "fruit3", "fruitn"]


@pytest.mark.skipif(not (STATIC / "yolo2xml" / "test.txt").exists(), reason="fixture missing")
def test_golden_yolo2xml_fixture(tmp_path):
    outs = convert(
        "yolo2xml",
        txts=STATIC / "yolo2xml" / "test.txt",
        imgs=STATIC / "yolo2xml" / "test.jpg",
        classes=STATIC / "yolo2xml" / "voc.names",
        out=tmp_path,
    )
    from convertmask.core.voc import read_voc

    ann = read_voc(outs[0])
    import cv2

    h, w = cv2.imread(str(STATIC / "yolo2xml" / "test.jpg")).shape[:2]
    # box denormalized with the image's own (w, h) — inside bounds, sane size
    xmin, ymin, xmax, ymax = ann.shapes[0].bbox()
    assert 0 <= xmin < xmax <= w and 0 <= ymin < ymax <= h


@pytest.mark.skipif(not (STATIC / "mask" / "1-2cvt.png").exists(), reason="fixture missing")
def test_golden_mask2json_fixture(tmp_path):
    outs = convert(
        "mask2json", imgs=STATIC / "1-2cvt.jpg", masks=STATIC / "mask" / "1-2cvt.png",
        out=tmp_path,
    )
    data = json.loads(outs[0].read_text(encoding="utf-8"))
    assert data["shapes"]
    for s in data["shapes"]:
        assert s["shape_type"] == "polygon"
        assert len(s["points"]) >= 3
