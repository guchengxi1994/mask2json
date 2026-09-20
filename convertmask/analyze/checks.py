"""Annotation-consistency checks.

Every check returns plain-data issues so the report (and the web UI) can
render them without importing image libraries. These are the checks that
would have caught the legacy tool's silent label corruption.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path

from convertmask.core.annotation import Annotation

ERROR = "error"
WARNING = "warning"

# boxes below this on either side are suspiciously small (matches json2xml)
SMALL_BOX_PX = 10.0
# same-class boxes more overlapping than this are near-duplicates
DUPLICATE_IOU = 0.9
# augmented objects whose area leaves this ratio band vs the original
AREA_DRIFT = (0.4, 2.5)


@dataclass
class Issue:
    code: str
    severity: str
    detail: str
    shape_index: int | None = None


@dataclass
class FileReport:
    file: str
    image: str | None
    width: int | None = None
    height: int | None = None
    issues: list[Issue] = field(default_factory=list)

    def add(self, code: str, severity: str, detail: str, shape_index: int | None = None):
        self.issues.append(Issue(code, severity, detail, shape_index))

    def to_dict(self) -> dict:
        d = asdict(self)
        d["issues"] = [asdict(i) for i in self.issues]
        return d


def iou(box_a: tuple[float, float, float, float], box_b: tuple[float, float, float, float]) -> float:
    xmin = max(box_a[0], box_b[0])
    ymin = max(box_a[1], box_b[1])
    xmax = min(box_a[2], box_b[2])
    ymax = min(box_a[3], box_b[3])
    inter = max(0.0, xmax - xmin) * max(0.0, ymax - ymin)
    union = (
        (box_a[2] - box_a[0]) * (box_a[3] - box_a[1])
        + (box_b[2] - box_b[0]) * (box_b[3] - box_b[1])
        - inter
    )
    return inter / union if union > 0 else 0.0


def check_annotation(
    ann: Annotation,
    file: str,
    image: str | None = None,
    image_size: tuple[int, int] | None = None,
    known_classes: set[str] | None = None,
) -> FileReport:
    """Run all per-annotation checks and return a :class:`FileReport`."""
    rep = FileReport(file=file, image=image, width=ann.width, height=ann.height)

    if not ann.shapes:
        rep.add("empty_annotation", WARNING, "no shapes in this annotation")
        return rep

    if image_size is not None:
        iw, ih = image_size
        if (iw, ih) != (ann.width, ann.height):
            rep.add(
                "size_mismatch",
                ERROR,
                f"annotation says {ann.width}x{ann.height}, image is {iw}x{ih}",
            )

    boxes = []
    for i, s in enumerate(ann.shapes):
        xmin, ymin, xmax, ymax = s.bbox()
        boxes.append((xmin, ymin, xmax, ymax))

        if xmax <= xmin or ymax <= ymin:
            rep.add(
                "degenerate_box", ERROR,
                f"{s.label!r}: zero/negative size ({xmax - xmin:.1f}x{ymax - ymin:.1f})", i,
            )
            continue
        if ann.width and (xmin < 0 or ymin < 0 or xmax > ann.width or ymax > ann.height):
            rep.add(
                "out_of_bounds", ERROR,
                f"{s.label!r}: box ({xmin:.0f},{ymin:.0f},{xmax:.0f},{ymax:.0f}) "
                f"outside {ann.width}x{ann.height}",
                i,
            )
        if (xmax - xmin) < SMALL_BOX_PX or (ymax - ymin) < SMALL_BOX_PX:
            rep.add(
                "tiny_object", WARNING,
                f"{s.label!r}: {xmax - xmin:.0f}x{ymax - ymin:.0f} px is below "
                f"{SMALL_BOX_PX:.0f} px",
                i,
            )
        if known_classes is not None and s.label not in known_classes:
            rep.add(
                "unknown_class", ERROR,
                f"label {s.label!r} not in the provided class file", i,
            )

    for i in range(len(boxes)):
        for j in range(i + 1, len(boxes)):
            if ann.shapes[i].label != ann.shapes[j].label:
                continue
            overlap = iou(boxes[i], boxes[j])
            if overlap > DUPLICATE_IOU:
                rep.add(
                    "duplicate_object", WARNING,
                    f"two {ann.shapes[i].label!r} boxes overlap with IoU {overlap:.2f}",
                    i,
                )
    return rep


def class_distribution(annotations: list[tuple[str, Annotation]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for _, ann in annotations:
        for s in ann.shapes:
            counts[s.label] = counts.get(s.label, 0) + 1
    return dict(sorted(counts.items(), key=lambda kv: -kv[1]))


def check_area_drift(
    baseline: dict[str, Annotation], current: list[tuple[str, Annotation]]
) -> list[Issue]:
    """Compare objects of augmented files against their original stems.

    Baseline keys are stems (e.g. ``a``); current entries may be
    ``a_aug0_rot30`` — matched by prefix. Flags objects whose total
    per-class area leaves a sane ratio band (drops from clipping, drift
    from unsynced transforms).
    """
    issues: list[Issue] = []
    for fname, ann in current:
        stem = Path(str(fname)).stem
        base = None
        # longest matching baseline stem prefix
        for b_stem in sorted(baseline, key=len, reverse=True):
            if stem == b_stem or stem.startswith(b_stem + "_aug"):
                base = baseline[b_stem]
                break
        if base is None:
            continue
        base_area: dict[str, float] = {}
        for s in base.shapes:
            xmin, ymin, xmax, ymax = s.bbox()
            base_area[s.label] = base_area.get(s.label, 0.0) + (xmax - xmin) * (ymax - ymin)
        cur_area: dict[str, float] = {}
        for s in ann.shapes:
            xmin, ymin, xmax, ymax = s.bbox()
            cur_area[s.label] = cur_area.get(s.label, 0.0) + (xmax - xmin) * (ymax - ymin)
        for label, area in cur_area.items():
            if label not in base_area:
                continue
            ratio = area / base_area[label] if base_area[label] > 0 else float("inf")
            if not (AREA_DRIFT[0] <= ratio <= AREA_DRIFT[1]):
                issues.append(
                    Issue(
                        code="area_drift",
                        severity=WARNING,
                        detail=f"{fname}: class {label!r} total area ratio "
                        f"{ratio:.2f} outside {AREA_DRIFT}",
                    )
                )
    return issues
