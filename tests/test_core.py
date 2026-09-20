"""Core IR tests: format round-trips must be geometrically lossless."""

from __future__ import annotations

import numpy as np

from convertmask.core.annotation import BACKGROUND, Annotation, Shape
from convertmask.core.b64 import decode_to_array, encode_image
from convertmask.core.classfile import class_map_from_names, load_class_map, save_class_map
from convertmask.core.colormap import color_for, label2rgb, label_colormap
from convertmask.core.imageio import read_image, read_mask, write_image
from convertmask.core.labelmap import annotation_label_map, label_to_shapes, shapes_to_label
from convertmask.core.voc import read_voc, write_voc


def _assert_bbox_close(shape: Shape, expected: tuple[float, ...], tol: float = 1.5):
    assert shape.bbox() == pytest_approx_tuple(expected, tol)


def pytest_approx_tuple(expected, tol):
    class _Cmp(tuple):
        def __eq__(self, other):
            return len(self) == len(other) and all(
                abs(a - b) <= tol for a, b in zip(self, other, strict=False)
            )

        def __repr__(self):
            return f"approx{tuple.__repr__(self)}"

    return _Cmp(expected)


# --------------------------------------------------------------------- #
# labelme JSON round trip


def test_labelme_round_trip(annotation: Annotation):
    data = annotation.to_labelme_dict("QUJD")
    ann2 = Annotation.from_labelme_dict(data)
    assert ann2.width == annotation.width
    assert ann2.height == annotation.height
    assert [s.label for s in ann2.shapes] == ["cat", "dog"]
    for s1, s2 in zip(annotation.shapes, ann2.shapes, strict=True):
        assert s1.points == s2.points
    # group_id must be a real null, not the legacy "null" string
    assert data["shapes"][0]["group_id"] is None


# --------------------------------------------------------------------- #
# VOC round trip


def test_voc_round_trip(tmp_path, annotation: Annotation):
    xml = write_voc(annotation, tmp_path / "a.xml", folder="TEST")
    ann2 = read_voc(xml)
    assert ann2.width == 120 and ann2.height == 80
    assert [s.label for s in ann2.shapes] == ["cat", "dog"]
    assert ann2.shapes[0].bbox() == (5, 10, 50, 40)
    assert ann2.shapes[1].bbox() == (60, 20, 110, 60)


def test_voc_zero_size_fallback(tmp_path, annotation: Annotation):
    """Files with 0x0 size (legacy widerface output) must fall back."""
    xml = write_voc(annotation, tmp_path / "a.xml")
    text = xml.read_text(encoding="utf-8")
    text = text.replace("<width>120</width>", "<width>0</width>")
    text = text.replace("<height>80</height>", "<height>0</height>")
    xml.write_text(text, encoding="utf-8")
    ann2 = read_voc(xml, fallback_size=(120, 80))
    assert (ann2.width, ann2.height) == (120, 80)


# --------------------------------------------------------------------- #
# YOLO round trip — the axis-swap regression test


def test_yolo_round_trip(annotation: Annotation):
    lines, names = annotation.to_yolo_lines()
    assert names == ["cat", "dog"]
    ann2 = Annotation.from_yolo_lines(lines, names, annotation.width, annotation.height)
    assert [s.label for s in ann2.shapes] == ["cat", "dog"]
    # non-square image: an axis swap would move the boxes
    _assert_bbox_close(ann2.shapes[0], (5, 10, 50, 40))
    _assert_bbox_close(ann2.shapes[1], (60, 20, 110, 60))


def test_yolo_values(annotation: Annotation):
    lines, _ = annotation.to_yolo_lines()
    cls, x, y, w, h = lines[0].split()
    assert int(cls) == 0
    # cat box: cx=27.5/120, cy=25/80, w=45/120, h=30/80
    assert abs(float(x) - 27.5 / 120) < 1e-4
    assert abs(float(y) - 25.0 / 80) < 1e-4
    assert abs(float(w) - 45.0 / 120) < 1e-4
    assert abs(float(h) - 30.0 / 80) < 1e-4


# --------------------------------------------------------------------- #
# label maps


def test_shapes_to_label_ids_by_first_appearance():
    shapes = [
        Shape(label="b", points=[[0, 0], [10, 0], [10, 10], [0, 10]]),
        Shape(label="a", points=[[20, 0], [30, 0], [30, 10], [20, 10]]),
    ]
    lbl, names = shapes_to_label(20, 40, shapes)
    assert names == [BACKGROUND, "b", "a"]
    assert lbl[5, 5] == 1  # class "b" got id 1 (first seen)
    assert lbl[5, 25] == 2


def test_shapes_to_label_overlap_later_wins():
    big = Shape(label="big", points=[[0, 0], [30, 0], [30, 30], [0, 30]])
    small = Shape(label="small", points=[[5, 5], [15, 5], [15, 15], [5, 15]])
    lbl, names = shapes_to_label(40, 40, [big, small])
    assert lbl[10, 10] == names.index("small")
    assert lbl[25, 25] == names.index("big")


def test_label_to_shapes_round_trip(class_mask: np.ndarray):
    names = [BACKGROUND, "one", "two"]
    shapes = label_to_shapes(class_mask, names)
    lbl2, names2 = shapes_to_label(class_mask.shape[0], class_mask.shape[1], shapes)
    # reconstructed regions must cover >95% of the original per class
    for value in (1, 2):
        inter = ((class_mask == value) & (lbl2 == value)).sum()
        union = ((class_mask == value) | (lbl2 == value)).sum()
        assert inter / union > 0.95
    assert names2 == names


def test_annotation_label_map_uses_class_table(annotation: Annotation):
    lbl, names = annotation_label_map(annotation)
    assert names == [BACKGROUND, "cat", "dog"]
    assert lbl[15, 20] == 1
    assert lbl[30, 80] == 2


# --------------------------------------------------------------------- #
# image IO


def test_image_write_read_round_trip(tmp_path, rgb_image: np.ndarray):
    p = write_image(tmp_path / "sub" / "img.png", rgb_image)
    back = read_image(p)
    assert back.shape == rgb_image.shape
    assert np.array_equal(back, rgb_image)


def test_image_io_nonascii_path(tmp_path, rgb_image: np.ndarray):
    p = tmp_path / "图片 folder" / "测试.png"
    write_image(p, rgb_image)
    assert np.array_equal(read_image(p), rgb_image)


def test_mask_values_preserved(tmp_path, class_mask: np.ndarray):
    p = write_image(tmp_path / "m.png", class_mask)
    assert np.array_equal(read_mask(p), class_mask)


def test_read_image_missing_raises(tmp_path):
    import pytest

    with pytest.raises(FileNotFoundError):
        read_image(tmp_path / "nope.png")


# --------------------------------------------------------------------- #
# base64


def test_b64_round_trip(rgb_image: np.ndarray, tmp_path):
    s = encode_image(rgb_image)
    back = decode_to_array(s)
    assert back is not None and back.shape == rgb_image.shape

    p = write_image(tmp_path / "x.png", rgb_image)
    s2 = encode_image(p)
    back2 = decode_to_array(s2)
    assert back2 is not None and back2.shape == rgb_image.shape


def test_b64_empty():
    assert decode_to_array(None) is None
    assert decode_to_array("") is None


# --------------------------------------------------------------------- #
# colormap


def test_colormap_distinct_and_stable():
    cmap = label_colormap(256)
    assert cmap.shape == (256, 3)
    assert (cmap[0] == 0).all()
    assert color_for(1) == tuple(int(v) for v in cmap[1])


def test_label2rgb_shapes(class_mask: np.ndarray, rgb_image: np.ndarray):
    out = label2rgb(class_mask, rgb_image)
    assert out.shape == rgb_image.shape
    out2 = label2rgb(class_mask, None)
    assert out2.shape == (*class_mask.shape, 3)


# --------------------------------------------------------------------- #
# class files


def test_classfile_txt_round_trip(tmp_path):
    p = tmp_path / "classes.txt"
    p.write_text("cat\ndog\n", encoding="utf-8")
    assert load_class_map(p) == {"cat": 1, "dog": 2}


def test_classfile_yaml_round_trip(tmp_path):
    p = save_class_map(tmp_path / "info.yaml", {"cat": 1, "dog": 255})
    mapping = load_class_map(p)
    assert mapping == {"cat": 1, "dog": 255}
    assert "_background_" not in mapping


def test_classfile_yaml_full_form(tmp_path):
    p = tmp_path / "info.yaml"
    p.write_text(
        "label_names:\n  _background_: 0\n  cat: 1\n  dog: 2\n", encoding="utf-8"
    )
    assert load_class_map(p) == {"cat": 1, "dog": 2}


def test_class_map_from_names_order():
    assert class_map_from_names(["b", "a", "b"]) == {"b": 1, "a": 2}
