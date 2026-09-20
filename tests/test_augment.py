"""Augmentation tests: labels must follow pixels, results must be reproducible."""

from __future__ import annotations

import json
from pathlib import Path

import cv2
import numpy as np
import pytest

from convertmask.augment import augment_images
from convertmask.augment.base import clip_polygon, transform_points
from convertmask.augment.basic import Flip, Rotation, Translation, Zoom, add_noise
from convertmask.core.annotation import Annotation, Shape
from tests.conftest import make_image


@pytest.fixture
def ann() -> Annotation:
    return Annotation(
        width=120, height=80, image_path=Path("a.jpg"),
        shapes=[
            Shape("cat", [[20, 20], [40, 20], [40, 50], [20, 50]]),
            Shape("dog", [[60, 10], [100, 10], [100, 60], [60, 60]]),
        ],
    )


def test_flip_maps_boxes_exactly():
    flip = Flip()
    img = make_image()
    ann = Annotation(
        width=120, height=80,
        shapes=[Shape("cat", [[20, 20], [40, 20], [40, 50], [20, 50]])],
    )
    outs = flip.variants(img, ann, np.random.default_rng(0))
    assert len(outs) == 3
    # horizontal: x' = w-1-x  ->  box [20,40] becomes [79,99]
    _, ann_h, _ = outs[0]
    xmin, ymin, xmax, ymax = ann_h.shapes[0].bbox()
    assert (xmin, xmax) == (120 - 1 - 40, 120 - 1 - 20)
    assert (ymin, ymax) == (20, 50)
    # vertical: y' = h-1-y
    _, ann_v, _ = outs[1]
    xmin, ymin, xmax, ymax = ann_v.shapes[0].bbox()
    assert (xmin, xmax) == (20, 40)
    assert (ymin, ymax) == (80 - 1 - 50, 80 - 1 - 20)


def test_rotation_box_tracks_corners():
    """45-degree rotation: the new box is the corner-mapped AABB, not smaller."""
    img = make_image(100, 100)  # rotation center = annotation center
    ann = Annotation(
        width=100, height=100,
        shapes=[Shape("cat", [[40, 40], [60, 40], [60, 60], [40, 60]])],
    )
    rot = Rotation(angle=45)
    (out_img, out_ann, _) = rot.variants(img, ann, np.random.default_rng(0))[0]
    xmin, ymin, xmax, ymax = out_ann.shapes[0].bbox()
    # center box [40,60]^2 rotated 45deg around (50,50): corners reach
    # 50 +- 10*sqrt(2) on both axes
    reach = 10 * 2**0.5
    assert abs(xmin - (50 - reach)) < 1.5
    assert abs(xmax - (50 + reach)) < 1.5
    assert abs(ymin - (50 - reach)) < 1.5
    assert abs(ymax - (50 + reach)) < 1.5


def test_translation_moves_boxes():
    img = make_image()
    ann = Annotation(width=120, height=80,
                     shapes=[Shape("cat", [[20, 20], [40, 20], [40, 50], [20, 50]])])
    (out_img, out_ann, _) = Translation(th=10, tv=5).variants(
        img, ann, np.random.default_rng(0)
    )[0]
    assert out_ann.shapes[0].bbox()[:2] == (30, 25)


def test_translation_drops_fully_shifted_objects():
    img = make_image()
    ann = Annotation(width=120, height=80,
                     shapes=[Shape("cat", [[20, 20], [40, 20], [40, 50], [20, 50]])])
    (out_img, out_ann, _) = Translation(th=-200, tv=0).variants(
        img, ann, np.random.default_rng(0)
    )[0]
    assert out_ann.shapes == []  # object fully outside: dropped, not clamped garbage


def test_zoom_scales_boxes():
    img = make_image()
    ann = Annotation(width=120, height=80,
                     shapes=[Shape("cat", [[20, 20], [40, 20], [40, 50], [20, 50]])])
    (out_img, out_ann, _) = Zoom(factor=2.0).variants(img, ann, np.random.default_rng(0))[0]
    xmin, ymin, xmax, ymax = out_ann.shapes[0].bbox()
    # zoom x2 about image center (60,40): x [20,40] -> [-20,20] -> clipped [0,20];
    # y [20,50] -> [0,60] stays inside
    assert (xmin, ymin, xmax, ymax) == (0, 0, 20, 60)


def test_noise_keeps_labels_and_ranges():
    img = make_image()
    out = add_noise(img, "gaussian", np.random.default_rng(1))
    assert out.shape == img.shape and out.dtype == np.uint8
    for kind in ("s&p", "speckle", "poisson"):
        add_noise(img, kind, np.random.default_rng(1))
    with pytest.raises(ValueError):
        add_noise(img, "nope", np.random.default_rng(1))


def test_clip_polygon_basic():
    square = np.array([[10, 10], [30, 10], [30, 30], [10, 30]], dtype=np.float64)
    clipped = clip_polygon(square, 20, 20)
    assert clipped is not None
    assert clipped[:, 0].max() <= 19 and clipped[:, 1].max() <= 19
    assert clip_polygon(np.array([[100, 100], [120, 100], [120, 120], [100, 120]], dtype=np.float64), 50, 50) is None


def test_transform_points_homogeneous():
    pts = np.array([[0.0, 0.0], [10.0, 0.0]])
    moved = transform_points(pts, np.array([[1.0, 0, 5], [0, 1.0, 7]]))
    assert np.allclose(moved, [[5, 7], [15, 7]])


# --------------------------------------------------------------------- #
# pipeline


def _write_env(tmp_path: Path) -> tuple[Path, Path]:
    imgs, labels = tmp_path / "imgs", tmp_path / "labels"
    imgs.mkdir(), labels.mkdir()
    cv2.imwrite(str(imgs / "a.jpg"), make_image()[..., ::-1])
    ann = Annotation(
        width=120, height=80, image_path=Path("a.jpg"),
        shapes=[
            Shape("cat", [[20, 20], [40, 20], [40, 50], [20, 50]]),
            Shape("dog", [[60, 10], [100, 10], [100, 60], [60, 60]]),
        ],
    )
    ann.save_labelme_json(labels / "a.json", "QUJD")
    return imgs, labels


def test_pipeline_json_labels_and_mask(tmp_path):
    imgs, labels = _write_env(tmp_path)
    out = tmp_path / "aug"
    written = augment_images(
        imgs, labels, methods=["translation", "noise"], number=2, seed=42,
        out=out, save_mask=True,
    )
    jpgs = [p for p in written if p.suffix == ".jpg"]
    jsons = [p for p in written if p.suffix == ".json"]
    masks = [p for p in written if p.name.endswith(".png")]
    assert len(jpgs) == 2 and len(jsons) == 2 and len(masks) == 2
    for j in jsons:
        data = json.loads(j.read_text(encoding="utf-8"))
        assert data["shapes"], "annotation must not be empty after light translate"
        assert data["imageData"]  # embedded augmented image
    for m in masks:
        mask = cv2.imread(str(m), cv2.IMREAD_GRAYSCALE)
        assert set(np.unique(mask)) <= {0, 1, 2}  # no invented class values


def test_pipeline_reproducible_with_seed(tmp_path):
    imgs, labels = _write_env(tmp_path)
    a = augment_images(imgs, labels, methods=["rotation", "zoom"], number=1,
                       seed=7, out=tmp_path / "a")
    b = augment_images(imgs, labels, methods=["rotation", "zoom"], number=1,
                       seed=7, out=tmp_path / "b")
    ja = [p for p in a if p.suffix == ".jpg"][0]
    jb = [p for p in b if p.suffix == ".jpg"][0]
    assert np.array_equal(cv2.imread(str(ja)), cv2.imread(str(jb)))


def test_pipeline_xml_labels(tmp_path):
    from convertmask.core.voc import write_voc

    imgs, labels = tmp_path / "imgs", tmp_path / "labels"
    imgs.mkdir(), labels.mkdir()
    cv2.imwrite(str(imgs / "a.jpg"), make_image()[..., ::-1])
    ann = Annotation(width=120, height=80, image_path=Path("a.jpg"),
                     shapes=[Shape("cat", [[20, 20], [40, 20], [40, 50], [20, 50]])])
    write_voc(ann, labels / "a.xml")
    written = augment_images(imgs, labels, methods=["noise"], number=1, seed=0,
                             out=tmp_path / "aug")
    xmls = [p for p in written if p.suffix == ".xml"]
    assert len(xmls) == 1
    from convertmask.core.voc import read_voc

    ann2 = read_voc(xmls[0])
    assert ann2.shapes[0].bbox() == (20, 20, 40, 50)  # noise: geometry unchanged


def test_pipeline_flip_fans_out_three_branches(tmp_path):
    imgs, labels = _write_env(tmp_path)
    written = augment_images(imgs, labels, methods=["flip"], number=1, seed=0,
                             out=tmp_path / "aug")
    jpgs = [p for p in written if p.suffix == ".jpg"]
    assert len(jpgs) == 3  # h, v, hv
    assert {p.stem.rsplit("_", 1)[-1] for p in jpgs} == {"h", "v", "hv"}


def test_pipeline_unlabeled(tmp_path):
    imgs, _ = _write_env(tmp_path)
    written = augment_images(imgs, None, methods=["noise"], number=1, out=tmp_path / "aug")
    assert len(written) == 1 and written[0].suffix == ".jpg"


def test_pipeline_unknown_method_raises(tmp_path):
    imgs, _ = _write_env(tmp_path)
    with pytest.raises(ValueError, match="unknown augmentation"):
        augment_images(imgs, None, methods=["nope"], out=tmp_path / "aug")


# --------------------------------------------------------------------- #
# every augmentation method must run end-to-end (labeled)

ALL_LABELED_METHODS = [
    "flip", "rotation", "translation", "zoom", "noise",
    "crop", "distort", "inpaint", "perspective", "resize",
]


@pytest.mark.parametrize("method", ALL_LABELED_METHODS)
def test_every_method_runs_labeled(tmp_path, method):
    imgs, labels = _write_env(tmp_path)
    written = augment_images(imgs, labels, methods=[method], number=1, seed=5,
                             out=tmp_path / "aug")
    jpgs = [p for p in written if p.suffix == ".jpg"]
    anns = [p for p in written if p.suffix in {".json", ".xml"}]
    assert jpgs, f"{method} produced no image"
    assert len(jpgs) == len(anns), f"{method}: image/annotation count mismatch"


def test_mixup_cutmix_with_other_image(rgb_image):
    from convertmask.augment import build

    ann = Annotation(width=120, height=80, image_path=Path("a.jpg"),
                     shapes=[Shape("cat", [[20, 20], [40, 20], [40, 50], [20, 50]])])
    rng = np.random.default_rng(0)
    for method, kwargs in (("mixup", {}), ("cutmix", {"factor": 0.3})):
        stage = build(method, {"other": make_image(60, 40), **kwargs})
        outs = stage.variants(make_image(), ann, rng)
        assert len(outs) == 1
        out_img, out_ann, tag = outs[0]
        assert out_img.shape[:2] == (80, 120)
        assert tag == method
