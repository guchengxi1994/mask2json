"""Analyzer tests: synthetic broken annotations must be caught."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from convertmask.analyze import analyze_dataset
from convertmask.analyze.checks import check_annotation, iou
from convertmask.analyze.image_metrics import image_metrics, metric_deltas
from convertmask.augment import augment_images
from convertmask.core.annotation import Annotation, Shape
from tests.conftest import make_image


def _ann(width=120, height=80, **shapes) -> Annotation:
    return Annotation(width=width, height=height, shapes=list(shapes.values()))


def test_iou_math():
    assert iou((0, 0, 10, 10), (0, 0, 10, 10)) == 1.0
    assert iou((0, 0, 10, 10), (20, 20, 30, 30)) == 0.0
    assert 0.1 < iou((0, 0, 10, 10), (5, 5, 15, 15)) < 0.2  # 25/175


def test_check_out_of_bounds_and_degenerate():
    ann = _ann(
        bad=Shape("cat", [[-10, 0], [50, 0], [50, 30], [-10, 30]]),
        degenerate=Shape("cat", [[10, 10], [10, 10], [10, 10], [10, 10]]),
    )
    rep = check_annotation(ann, "a.json")
    codes = [i.code for i in rep.issues]
    assert "out_of_bounds" in codes
    assert "degenerate_box" in codes
    assert all(i.severity == "error" for i in rep.issues if i.code in
               {"out_of_bounds", "degenerate_box"})


def test_check_tiny_and_duplicate_and_empty():
    tiny = _ann(t=Shape("cat", [[5, 5], [12, 5], [12, 12], [5, 12]]))
    assert "tiny_object" in [i.code for i in check_annotation(tiny, "a.json").issues]

    dup = _ann(
        a=Shape("cat", [[10, 10], [50, 10], [50, 50], [10, 50]]),
        b=Shape("cat", [[11, 10], [50, 10], [50, 50], [11, 50]]),
    )
    assert "duplicate_object" in [i.code for i in check_annotation(dup, "a.json").issues]

    empty = _ann()
    assert "empty_annotation" in [i.code for i in check_annotation(empty, "a.json").issues]


def test_check_unknown_class_and_size_mismatch():
    ann = _ann(a=Shape("cat", [[10, 10], [60, 10], [60, 50], [10, 50]]))
    rep = check_annotation(ann, "a.json", image_size=(100, 70),
                           known_classes={"dog", "bird"})
    codes = [i.code for i in rep.issues]
    assert "size_mismatch" in codes
    assert "unknown_class" in codes


def test_image_metrics_and_deltas():
    rng = np.random.default_rng(0)
    flat = np.full((50, 50, 3), 128, dtype=np.uint8)
    m1 = image_metrics(flat)
    assert m1["brightness"] == 128.0
    assert m1["contrast"] < 1.0
    noisy = rng.integers(0, 256, (50, 50, 3)).astype(np.uint8)
    m2 = image_metrics(noisy)
    assert m2["noise"] > m1["noise"]
    d = metric_deltas(m1, m2)
    assert d["noise"]["delta"] > 0
    assert d["brightness"]["ratio"] is not None


# --------------------------------------------------------------------- #
# end-to-end


def _write_dataset(tmp_path: Path) -> tuple[Path, Path]:
    imgs, annos = tmp_path / "imgs", tmp_path / "annos"
    imgs.mkdir(), annos.mkdir()
    import cv2

    cv2.imwrite(str(imgs / "good.jpg"), make_image()[..., ::-1])
    cv2.imwrite(str(imgs / "bad.jpg"), make_image(200, 150)[..., ::-1])

    good = Annotation(
        width=120, height=80, image_path=Path("good.jpg"),
        shapes=[Shape("cat", [[20, 20], [60, 20], [60, 50], [20, 50]])],
    )
    good.save_labelme_json(annos / "good.json")
    bad = Annotation(
        width=120, height=80, image_path=Path("bad.jpg"),
        shapes=[Shape("cat", [[100, 100], [180, 100], [180, 140], [100, 140]])],
    )
    bad.save_labelme_json(annos / "bad.json")
    return imgs, annos


def test_analyze_dataset_report(tmp_path):
    imgs, annos = _write_dataset(tmp_path)
    report = analyze_dataset(annos, imgs, out=tmp_path / "analysis")
    assert report["summary"]["annotations"] == 2
    assert report["summary"]["errors"] >= 1  # bad.json: out_of_bounds + size_mismatch
    codes = report["summary"]["issue_counts"]
    assert codes.get("out_of_bounds") == 1
    assert codes.get("size_mismatch") == 1
    assert (tmp_path / "analysis" / "report.json").exists()
    overlays = list((tmp_path / "analysis" / "overlays").glob("*.png"))
    assert len(overlays) == 2
    good_entry = next(f for f in report["files"] if f["file"] == "good.json")
    assert "metrics" in good_entry and "sharpness" in good_entry["metrics"]


def test_analyze_unknown_classes_via_classfile(tmp_path):
    imgs, annos = _write_dataset(tmp_path)
    (tmp_path / "classes.txt").write_text("dog\n", encoding="utf-8")
    report = analyze_dataset(annos, imgs, classes=tmp_path / "classes.txt",
                             out=tmp_path / "analysis", save_overlays=False)
    assert report["summary"]["issue_counts"].get("unknown_class", 0) >= 2


def test_analyze_with_baseline_after_augmentation(tmp_path):
    imgs, annos = _write_dataset(tmp_path)
    augment_images(imgs, annos, methods=["rotation"], number=1, seed=5,
                   out=tmp_path / "aug")
    report = analyze_dataset(
        tmp_path / "aug", tmp_path / "aug", out=tmp_path / "analysis",
        save_overlays=False, baseline=annos, baseline_imgs=imgs,
    )
    comp = report["comparison"]
    assert "class_drift" in comp
    # rotation may clip objects: drift tracking must at least run and be well-formed
    assert isinstance(comp["area_drift"], list)
    json.dumps(comp)  # serializable
