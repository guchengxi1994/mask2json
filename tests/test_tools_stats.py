"""Tests for train/val split and dataset statistics/health."""

from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np

from convertmask.analyze.stats import (
    dataset_stats,
    dhash,
    find_duplicate_images,
    hamming,
    health_score,
)
from convertmask.cli import main
from convertmask.core.annotation import Annotation, Shape
from convertmask.tools import train_val_split
from tests.conftest import make_image

# --------------------------------------------------------------------- #
# train/val split


def _write_yolo_dir(tmp_path: Path, n_files: int = 20) -> Path:
    d = tmp_path / "labels"
    d.mkdir()
    np.random.default_rng(0)
    for i in range(n_files):
        lines = []
        # class 0 in every file; class 1 in every 4th; class 2 in one file only
        lines.append("0 0.5 0.5 0.2 0.2")
        if i % 4 == 0:
            lines.append("1 0.3 0.3 0.1 0.1")
        if i == 7:
            lines.append("2 0.7 0.7 0.1 0.1")
        (d / f"img{i}.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return d


def test_split_no_overlap_and_coverage(tmp_path):
    d = _write_yolo_dir(tmp_path)
    result = train_val_split(d, val_ratio=0.2, seed=42)
    train, val = set(result["train"]), set(result["val"])
    assert not (train & val), "a file landed in both sets"
    assert train | val == {str(p) for p in d.glob("*.txt")}
    # rare class (2) has a single occurrence: quota 0, stays in train
    # (the model must see it; a singleton class cannot be split)
    rare_file = str(d / "img7.txt")
    assert rare_file in train
    # class 1 appears in 5 files: at least one of them in val
    class1_files = {str(d / f"img{i}.txt") for i in range(20) if i % 4 == 0}
    assert class1_files & val


def test_split_deterministic_with_seed(tmp_path):
    d = _write_yolo_dir(tmp_path)
    a = train_val_split(d, val_ratio=0.2, seed=7)
    b = train_val_split(d, val_ratio=0.2, seed=7)
    assert a == b


def test_split_ratio_and_outputs(tmp_path):
    d = _write_yolo_dir(tmp_path, n_files=50)
    out = tmp_path / "split"
    result = train_val_split(d, out=out, val_ratio=0.1, seed=1)
    total = len(result["train"]) + len(result["val"])
    assert total == 50
    assert 0 < len(result["val"]) / total <= 0.25  # ~10%, stratification slack
    assert (out / "train.txt").read_text().count("\n") == len(result["train"])
    assert (out / "val.txt").read_text().count("\n") == len(result["val"])


def test_split_rejects_bad_ratio(tmp_path):
    d = _write_yolo_dir(tmp_path, n_files=3)
    import pytest

    with pytest.raises(ValueError, match="val_ratio"):
        train_val_split(d, val_ratio=1.5)


def test_cli_split(tmp_path, capsys):
    d = _write_yolo_dir(tmp_path)
    rc = main(["split", "--txts", str(d), "--out", str(tmp_path / "s"),
               "--val-ratio", "0.2", "--seed", "3"])
    assert rc == 0
    assert "train:" in capsys.readouterr().out
    assert (tmp_path / "s" / "train.txt").exists()


# --------------------------------------------------------------------- #
# dataset stats


def _ann(shapes: list[Shape], width=100, height=100) -> Annotation:
    return Annotation(width=width, height=height, shapes=shapes)


def test_dataset_stats_pos_neg_and_balance():
    anns = [
        (Path("a.json"), _ann([Shape("cat", [[10, 10], [60, 10], [60, 60], [10, 60]])])),
        (Path("b.json"), _ann([Shape("cat", [[5, 5], [40, 5], [40, 40], [5, 40]])])),
        (Path("c.json"), _ann([])),  # negative sample
    ]
    stats = dataset_stats(anns)
    assert stats["annotations"] == 3
    assert stats["positive_images"] == 2
    assert stats["negative_images"] == 1
    assert stats["pos_neg_ratio"] == "2:1"
    assert stats["negative_ratio"] > 0.3
    assert stats["objects"] == 2
    assert stats["classes"] == 1
    # boxes cover 50x50 (25%) and 35x35 (12.25%) of 100x100 -> mean ~18.6%
    assert 0.15 < stats["foreground_ratio_mean"] < 0.22


def test_dataset_stats_imbalance_and_tiny():
    anns = [
        (Path("a.json"), _ann([
            Shape("common", [[10, 10], [60, 10], [60, 60], [10, 60]]),
            Shape("common", [[5, 5], [40, 5], [40, 40], [5, 40]]),
            Shape("rare", [[10, 10], [60, 10], [60, 60], [10, 60]]),
            Shape("tiny", [[1, 1], [5, 1], [5, 5], [1, 5]]),  # 4px -> tiny
        ])),
    ]
    stats = dataset_stats(anns)
    assert stats["class_counts"] == {"common": 2, "rare": 1, "tiny": 1}
    assert stats["imbalance_ratio"] == 2.0
    assert stats["tiny_object_fraction"] == 0.25


def test_health_score_penalties():
    good = health_score(0, 0, {"imbalance_ratio": None, "negative_ratio": 0.0,
                               "tiny_object_fraction": 0.0})
    assert good["score"] == 100 and good["grade"] == "A"

    bad = health_score(10, 30, {"imbalance_ratio": 1000, "negative_ratio": 0.8,
                                "tiny_object_fraction": 0.5}, duplicates=3)
    assert bad["score"] < 40 and bad["grade"] == "D"
    assert bad["penalties"]["errors"] == 40  # capped
    assert bad["penalties"]["warnings"] == 20  # capped
    assert bad["penalties"]["duplicate_images"] == 15


def test_dhash_and_duplicates(tmp_path):
    img = make_image()
    same = img.copy()
    different = np.full_like(img, 200)

    a, b, c = tmp_path / "a.jpg", tmp_path / "b.jpg", tmp_path / "c.jpg"
    for p, arr in ((a, img), (b, same), (c, different)):
        cv2.imwrite(str(p), arr[..., ::-1])

    assert hamming(dhash(img), dhash(same)) == 0
    assert hamming(dhash(img), dhash(different)) > 4

    pairs = find_duplicate_images([a, b, c])
    assert len(pairs) == 1
    assert {Path(pairs[0]["a"]).name, Path(pairs[0]["b"]).name} == {"a.jpg", "b.jpg"}


def test_report_contains_stats_and_health(tmp_path):
    from convertmask.analyze import analyze_dataset

    annos = tmp_path / "annos"
    annos.mkdir()
    Annotation(width=100, height=100, shapes=[]).save_labelme_json(annos / "neg.json")
    Annotation(width=100, height=100, shapes=[
        Shape("cat", [[10, 10], [60, 10], [60, 60], [10, 60]])
    ]).save_labelme_json(annos / "pos.json")
    report = analyze_dataset(annos, out=tmp_path / "r", save_overlays=False)
    assert report["stats"]["negative_images"] == 1
    assert report["health"]["score"] <= 100
    assert "penalties" in report["health"]
    assert report["duplicates"] == []
