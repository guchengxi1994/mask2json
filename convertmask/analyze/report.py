"""Dataset analysis: consistency checks + image metrics + overlays + report."""

from __future__ import annotations

import json
import logging
from pathlib import Path

from convertmask.analyze.checks import (
    ERROR,
    check_annotation,
    check_area_drift,
    class_distribution,
)
from convertmask.analyze.image_metrics import image_metrics, metric_deltas
from convertmask.analyze.overlay import save_overlay
from convertmask.analyze.stats import dataset_stats, find_duplicate_images, health_score
from convertmask.converters.common import collect_files, collect_images
from convertmask.core.annotation import Annotation
from convertmask.core.classfile import load_class_map
from convertmask.core.imageio import image_size, read_image
from convertmask.core.voc import read_voc

logger = logging.getLogger(__name__)


def _load_annotations(annos: Path) -> list[tuple[Path, Annotation]]:
    files = collect_files(annos, {".json", ".xml"})
    parsed = []
    for f in files:
        ann = read_voc(f) if f.suffix == ".xml" else Annotation.load_labelme_json(f)
        parsed.append((f, ann))
    return parsed


def analyze_dataset(
    annos: Path | str,
    imgs: Path | str | None = None,
    classes: Path | str | None = None,
    out: Path | str | None = None,
    baseline: Path | str | None = None,
    baseline_imgs: Path | str | None = None,
    save_overlays: bool = True,
) -> dict:
    """Analyze a dataset and (optionally) write ``report.json`` + overlays.

    ``baseline`` points at another annotation set (e.g. before augmentation)
    for class-drift / area-drift comparisons; ``baseline_imgs`` is the image
    set belonging to the baseline annotations and enables metric deltas.
    """
    annos = Path(annos)
    parsed = _load_annotations(annos)
    if not parsed:
        raise ValueError(f"no .json/.xml annotations in {annos}")

    known = set(load_class_map(classes)) if classes else None
    image_files = collect_images(imgs) if imgs else []
    images_by_stem = {p.stem: p for p in image_files}

    out = Path(out) if out else annos.parent / "analysis"
    overlay_dir = out / "overlays"

    files_section = []
    n_errors = n_warnings = 0
    issue_counts: dict[str, int] = {}

    for f, ann in parsed:
        img_path = images_by_stem.get(f.stem)
        size_ = image_size(img_path) if img_path else None
        rep = check_annotation(ann, file=f.name, image=img_path.name if img_path else None,
                               image_size=size_, known_classes=known)
        entry = rep.to_dict()
        if img_path:
            entry["metrics"] = image_metrics(read_image(img_path))
            bad = {i.shape_index for i in rep.issues if i.shape_index is not None}
            if save_overlays:
                save_overlay(img_path, ann, overlay_dir / f"{f.stem}_overlay.png", bad)
        for issue in rep.issues:
            if issue.severity == ERROR:
                n_errors += 1
            else:
                n_warnings += 1
            issue_counts[issue.code] = issue_counts.get(issue.code, 0) + 1
        files_section.append(entry)

    report: dict = {
        "summary": {
            "annotations": len(parsed),
            "images": len(image_files),
            "errors": n_errors,
            "warnings": n_warnings,
            "issue_counts": dict(sorted(issue_counts.items(), key=lambda kv: -kv[1])),
            "class_distribution": class_distribution(parsed),
        },
        "files": files_section,
    }

    stats = dataset_stats(parsed)
    duplicates = find_duplicate_images(image_files) if image_files else []
    report["stats"] = stats
    report["duplicates"] = duplicates
    report["health"] = health_score(n_errors, n_warnings, stats, len(duplicates))

    if baseline is not None:
        base_imgs_by_stem = (
            {p.stem: p for p in collect_images(baseline_imgs)} if baseline_imgs else {}
        )
        report["comparison"] = _compare(baseline, parsed, images_by_stem, base_imgs_by_stem)

    out.mkdir(parents=True, exist_ok=True)
    (out / "report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    logger.info("analysis written to %s", out / "report.json")
    return report


def _compare(
    baseline_dir: Path,
    current: list[tuple[Path, Annotation]],
    current_imgs_by_stem: dict[str, Path],
    base_imgs_by_stem: dict[str, Path],
) -> dict:
    base_parsed = _load_annotations(baseline_dir)
    base_dist = class_distribution(base_parsed)
    cur_dist = class_distribution(current)

    drift = {}
    for label in set(base_dist) | set(cur_dist):
        b, c = base_dist.get(label, 0), cur_dist.get(label, 0)
        if b == 0 and c == 0:
            continue
        drift[label] = {
            "baseline": b,
            "current": c,
            "delta": c - b,
            "ratio": round(c / b, 3) if b else None,
        }

    base_by_stem = {f.stem: ann for f, ann in base_parsed}
    area_issues = check_area_drift(base_by_stem, current)

    # metric deltas where both image sets contain the same stem
    deltas = {}
    for stem in base_imgs_by_stem:
        if stem not in current_imgs_by_stem:
            continue
        deltas[stem] = metric_deltas(
            image_metrics(read_image(base_imgs_by_stem[stem])),
            image_metrics(read_image(current_imgs_by_stem[stem])),
        )

    return {
        "class_drift": drift,
        "area_drift": [
            {"code": i.code, "severity": i.severity, "detail": i.detail}
            for i in area_issues
        ],
        "metric_deltas": deltas,
    }
