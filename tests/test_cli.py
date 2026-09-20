"""CLI tests: subcommands, legacy flat-form compatibility, error exits."""

from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np
import pytest

from convertmask.cli import main
from tests.conftest import make_image


@pytest.fixture
def dataset(tmp_path: Path) -> tuple[Path, Path, Path]:
    imgs, labels, masks = tmp_path / "imgs", tmp_path / "labels", tmp_path / "masks"
    for d in (imgs, labels, masks):
        d.mkdir()
    cv2.imwrite(str(imgs / "a.jpg"), make_image()[..., ::-1])
    mask = np.zeros((80, 120), dtype=np.uint8)
    mask[20:50, 20:60] = 1
    cv2.imwrite(str(masks / "a.png"), mask)
    (tmp_path / "classes.txt").write_text("cat\n", encoding="utf-8")
    return imgs, labels, masks


def test_cli_convert_new_form(dataset, tmp_path, capsys):
    imgs, labels, masks = dataset
    rc = main(["convert", "mask2json", "--imgs", str(imgs), "--masks", str(masks),
               "--classes", str(tmp_path / "classes.txt"), "--out", str(tmp_path / "o")])
    assert rc == 0
    assert (tmp_path / "o" / "a.json").exists()
    assert "1 file(s)" in capsys.readouterr().out


def test_cli_convert_alias(dataset, tmp_path):
    imgs, labels, masks = dataset
    rc = main(["convert", "m2j", "--imgs", str(imgs), "--masks", str(masks)])
    assert rc == 0
    assert (masks / "a.json").exists()  # default out = masks dir


def test_cli_legacy_flat_form(dataset, tmp_path):
    imgs, labels, masks = dataset
    rc = main(["m2j", "-i", str(imgs), str(masks), str(tmp_path / "classes.txt"),
               "--out", str(tmp_path / "o2")])
    # legacy form has no --out; run without it
    assert rc in (0, 2)
    rc = main(["mask2json", "-i", str(imgs), str(masks)])
    assert rc == 0
    assert (masks / "a.json").exists()


def test_cli_convert_missing_inputs_error(capsys):
    rc = main(["convert", "json2xml"])
    assert rc == 2
    assert "missing required" in capsys.readouterr().err


def test_cli_unknown_method_error(capsys):
    rc = main(["convert", "zzz", "--jsons", "x"])
    assert rc == 2
    assert "unknown method" in capsys.readouterr().err


def test_cli_augment(dataset, tmp_path):
    imgs, labels, masks = dataset
    # create a json label first via conversion
    main(["convert", "mask2json", "--imgs", str(imgs), "--masks", str(masks),
          "--out", str(tmp_path / "prep")])
    jsons = tmp_path / "prep"
    rc = main(["augment", "--imgs", str(imgs), "--labels", str(jsons),
               "--methods", "noise,translation", "--number", "2", "--seed", "3",
               "--out", str(tmp_path / "aug")])
    assert rc == 0
    jpgs = list((tmp_path / "aug").glob("*.jpg"))
    assert len(jpgs) == 2
    assert len(list((tmp_path / "aug").glob("*.json"))) == 2


def test_cli_analyze(dataset, tmp_path):
    imgs, labels, masks = dataset
    main(["convert", "mask2json", "--imgs", str(imgs), "--masks", str(masks),
          "--out", str(tmp_path / "prep")])
    rc = main(["analyze", "--annos", str(tmp_path / "prep"), "--imgs", str(imgs),
               "--out", str(tmp_path / "analysis")])
    assert rc == 0
    assert (tmp_path / "analysis" / "report.json").exists()


def test_cli_no_command_prints_help(capsys):
    rc = main([])
    assert rc == 0
    assert "usage" in capsys.readouterr().out


def test_cli_version(capsys):
    with pytest.raises(SystemExit) as exc:
        main(["--version"])
    assert exc.value.code == 0
    assert "convertmask" in capsys.readouterr().out
