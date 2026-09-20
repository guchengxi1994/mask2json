"""Dataset-level statistics and a health score.

The health score is a transparent 0-100 composite: start at 100 and
subtract documented penalties —

    errors           min(40, 5 per error)
    warnings         min(20, 1 per warning)
    class imbalance  up to 15, from log10(max/min class count)
    negative images  up to 10, when >50% of images have no objects
    tiny objects     up to 10, when >10% of objects are below 10 px

Grades: A >= 90, B >= 75, C >= 60, D below. Every component is included
in the report so the number is never a black box.
"""

from __future__ import annotations

import logging
from pathlib import Path

import cv2
import numpy as np

from convertmask.analyze.checks import SMALL_BOX_PX
from convertmask.core.annotation import Annotation

logger = logging.getLogger(__name__)

# dhash pairs at or below this hamming distance count as near-duplicates
DUPLICATE_HAMMING = 4
# skip duplicate scan above this many images (O(n^2) comparisons)
MAX_DUPLICATE_SCAN = 1000


def dataset_stats(
    annotations: list[tuple[Path, Annotation]],
) -> dict:
    """Compute dataset-level statistics from parsed annotations.

    ``negative'' images are images whose annotation has no shapes
    (background-only samples for detection training).
    """
    n = len(annotations)
    positives = sum(1 for _, ann in annotations if ann.shapes)
    negatives = n - positives
    objects = sum(len(ann.shapes) for _, ann in annotations)

    per_image = [len(ann.shapes) for _, ann in annotations]
    class_counts: dict[str, int] = {}
    tiny = 0
    foreground_ratios = []
    for _, ann in annotations:
        for s in ann.shapes:
            class_counts[s.label] = class_counts.get(s.label, 0) + 1
            xmin, ymin, xmax, ymax = s.bbox()
            if (xmax - xmin) < SMALL_BOX_PX or (ymax - ymin) < SMALL_BOX_PX:
                tiny += 1
        if ann.shapes and ann.width and ann.height:
            area = ann.width * ann.height
            covered = sum(
                max(0.0, (s.bbox()[2] - s.bbox()[0]) * (s.bbox()[3] - s.bbox()[1]))
                for s in ann.shapes
            )
            # bbox areas may overlap; cap at 1.0 (documented approximation)
            foreground_ratios.append(min(1.0, covered / area))

    counts = sorted(class_counts.values(), reverse=True)
    imbalance = (counts[0] / counts[-1]) if counts and counts[-1] > 0 else None

    return {
        "annotations": n,
        "positive_images": positives,
        "negative_images": negatives,
        "negative_ratio": round(negatives / n, 4) if n else 0.0,
        "pos_neg_ratio": f"{positives}:{negatives}" if negatives else f"{positives}:0",
        "objects": objects,
        "objects_per_image": {
            "mean": round(objects / n, 2) if n else 0.0,
            "median": float(np.median(per_image)) if per_image else 0.0,
            "max": max(per_image) if per_image else 0,
        },
        "classes": len(class_counts),
        "class_counts": dict(
            sorted(class_counts.items(), key=lambda kv: -kv[1])
        ),
        "imbalance_ratio": round(imbalance, 2) if imbalance else None,
        "tiny_object_fraction": round(tiny / objects, 4) if objects else 0.0,
        "foreground_ratio_mean": round(
            float(np.mean(foreground_ratios)) if foreground_ratios else 0.0, 4
        ),
    }


def health_score(
    errors: int, warnings: int, stats: dict, duplicates: int = 0
) -> dict:
    """Score a dataset 0-100 from issue counts and statistics."""
    p_error = min(40, errors * 5)
    p_warning = min(20, warnings)

    imbalance = stats.get("imbalance_ratio")
    p_imbalance = 0.0
    if imbalance and imbalance > 1:
        p_imbalance = min(15.0, 15.0 * np.log10(imbalance) / 2.0)

    neg_ratio = stats.get("negative_ratio", 0.0)
    p_negative = max(0.0, min(10.0, (neg_ratio - 0.5) * 20.0)) if neg_ratio > 0.5 else 0.0

    tiny = stats.get("tiny_object_fraction", 0.0)
    p_tiny = min(10.0, max(0.0, (tiny - 0.1) * 25.0)) if tiny > 0.1 else 0.0

    p_duplicates = min(15, duplicates * 5)

    score = max(
        0, min(100, round(100 - p_error - p_warning - p_imbalance - p_negative
                          - p_tiny - p_duplicates))
    )
    grade = "A" if score >= 90 else "B" if score >= 75 else "C" if score >= 60 else "D"
    return {
        "score": score,
        "grade": grade,
        "penalties": {
            "errors": p_error,
            "warnings": p_warning,
            "class_imbalance": round(p_imbalance, 1),
            "negative_images": round(p_negative, 1),
            "tiny_objects": round(p_tiny, 1),
            "duplicate_images": p_duplicates,
        },
    }


# --------------------------------------------------------------------- #
# near-duplicate image detection (dhash)


def dhash(img: np.ndarray, hash_size: int = 8) -> int:
    """Difference hash: 64-bit perceptual fingerprint of an image."""
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY) if img.ndim == 3 else img
    resized = cv2.resize(gray, (hash_size + 1, hash_size))
    diff = resized[:, 1:] > resized[:, :-1]
    bits = np.packbits(diff.flatten())
    return int(bits.view(np.uint64)[0])


def hamming(a: int, b: int) -> int:
    return bin(a ^ b).count("1")


def find_duplicate_images(
    image_paths: list[Path], threshold: int = DUPLICATE_HAMMING
) -> list[dict]:
    """Return near-duplicate image pairs (dhash hamming distance).

    Particularly relevant for augmented/synthetic datasets, where the same
    source image (or trivial variants of it) can slip in multiple times.
    """
    from convertmask.core.imageio import read_image

    paths = [Path(p) for p in image_paths]
    if len(paths) > MAX_DUPLICATE_SCAN:
        logger.warning(
            "duplicate scan skipped: %d images > cap of %d", len(paths), MAX_DUPLICATE_SCAN
        )
        return []
    hashes: list[tuple[Path, int]] = []
    for p in paths:
        try:
            hashes.append((p, dhash(read_image(p))))
        except (ValueError, FileNotFoundError, cv2.error):
            continue
    pairs = []
    for i in range(len(hashes)):
        for j in range(i + 1, len(hashes)):
            dist = hamming(hashes[i][1], hashes[j][1])
            if dist <= threshold:
                pairs.append({
                    "a": str(hashes[i][0]),
                    "b": str(hashes[j][0]),
                    "hamming": dist,
                })
    return pairs
