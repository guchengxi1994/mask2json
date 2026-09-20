"""Stratified train/val split for YOLO-format label directories.

Rewrite of the legacy ``train_val_dataset_split.yololike``: per-class val
quotas are computed once from the whole corpus (the legacy tool reset
state between files), assignment is seeded-deterministic, and no file can
land in both sets.
"""

from __future__ import annotations

import random
import re
from pathlib import Path

_LINE_RE = re.compile(r"^\s*(-?\d+)\s+[\d.]+\s+[\d.]+\s+[\d.]+\s+[\d.]+")


def _read_class_counts(txt_files: list[Path]) -> dict[Path, dict[int, int]]:
    counts: dict[Path, dict[int, int]] = {}
    for p in txt_files:
        per_file: dict[int, int] = {}
        for line in p.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not _LINE_RE.match(line):
                continue
            cls = int(line.split()[0])
            per_file[cls] = per_file.get(cls, 0) + 1
        counts[p] = per_file
    return counts


def train_val_split(
    txts: Path | str,
    out: Path | str | None = None,
    val_ratio: float = 0.1,
    seed: int | None = None,
) -> dict:
    """Split YOLO label files into train/val sets, stratified per class.

    Rare classes are placed first so every class with at least two
    occurrences gets a val sample whenever file granularity allows.
    Writes ``<out>/train.txt`` and ``<out>/val.txt`` and returns
    ``{"train": [...], "val": [...], "class_counts": {...}}``.
    """
    from convertmask.converters.common import collect_files

    txt_files = [
        p for p in collect_files(txts, {".txt"}) if p.name not in
        {"labels.txt", "classes.txt", "train.txt", "val.txt"}
    ]
    if not txt_files:
        raise ValueError(f"no YOLO label txt files in {txts}")
    if not 0 < val_ratio < 1:
        raise ValueError(f"val_ratio must be in (0, 1), got {val_ratio}")

    counts = _read_class_counts(txt_files)
    totals: dict[int, int] = {}
    for per_file in counts.values():
        for cls, n in per_file.items():
            totals[cls] = totals.get(cls, 0) + n

    rng = random.Random(seed)
    files = sorted(txt_files)
    rng.shuffle(files)

    # rarest classes decide first: their carrier files are scarce
    class_order = sorted(totals, key=lambda c: (totals[c], c))
    quota = {
        c: (max(1, round(totals[c] * val_ratio)) if totals[c] > 1 else 0)
        for c in totals
    }
    val_files: set[Path] = set()
    for cls in class_order:
        remaining = quota[cls] - sum(counts[p].get(cls, 0) for p in val_files)
        if remaining <= 0:
            continue
        # prefer unassigned files with the highest share of this class
        candidates = [
            p for p in files if p not in val_files and counts[p].get(cls)
        ]
        candidates.sort(key=lambda p: (-counts[p][cls] / sum(counts[p].values()), p))
        for p in candidates:
            if remaining <= 0:
                break
            val_files.add(p)
            remaining -= counts[p][cls]

    train = [p for p in files if p not in val_files]
    val = [p for p in files if p in val_files]
    if not train:
        raise ValueError("every file ended up in val; use a smaller val_ratio")

    if out is not None:
        out = Path(out)
        out.mkdir(parents=True, exist_ok=True)
        (out / "train.txt").write_text(
            "".join(f"{p}\n" for p in train), encoding="utf-8")
        (out / "val.txt").write_text(
            "".join(f"{p}\n" for p in val), encoding="utf-8")

    return {
        "train": [str(p) for p in train],
        "val": [str(p) for p in val],
        "class_counts": {str(c): n for c, n in sorted(totals.items())},
    }
