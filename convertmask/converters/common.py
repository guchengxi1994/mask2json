"""Shared helpers for converters: input collection and stem pairing."""

from __future__ import annotations

from pathlib import Path

from convertmask import SUPPORTED_CLASSFILE_EXTS, SUPPORTED_IMG_EXTS
from convertmask.core.classfile import load_class_map


def collect_files(src: Path | str, exts: set[str]) -> list[Path]:
    """Collect files with the given extensions from a file or directory.

    Raises ``FileNotFoundError`` for missing paths and ``ValueError`` when a
    single file has an unexpected extension.
    """
    src = Path(src)
    if src.is_file():
        if src.suffix.lower() not in exts:
            raise ValueError(f"unexpected file type {src.suffix!r}: {src}")
        return [src]
    if not src.is_dir():
        raise FileNotFoundError(f"not a file or directory: {src}")
    return sorted(p for p in src.iterdir() if p.is_file() and p.suffix.lower() in exts)


def collect_images(src: Path | str) -> list[Path]:
    return collect_files(src, SUPPORTED_IMG_EXTS)


def pair_by_stem(primary: list[Path], secondary: list[Path]) -> list[tuple[Path, Path]]:
    """Pair files by filename stem; raise listing unmatched primary files."""
    by_stem = {p.stem: p for p in secondary}
    pairs, missing = [], []
    for p in primary:
        match = by_stem.get(p.stem)
        if match is None:
            missing.append(p.name)
        else:
            pairs.append((p, match))
    if missing:
        raise FileNotFoundError(
            f"no matching file for {len(missing)} item(s): {', '.join(missing[:10])}"
            + (" ..." if len(missing) > 10 else "")
        )
    return pairs


def load_classes(classes: Path | str | None) -> dict[str, int] | None:
    """Load an optional class file (txt or labelme info.yaml)."""
    if classes is None or str(classes) == "":
        return None
    classes = Path(classes)
    if classes.suffix.lower() not in SUPPORTED_CLASSFILE_EXTS:
        raise ValueError(
            f"class file must be one of {sorted(SUPPORTED_CLASSFILE_EXTS)}: {classes}"
        )
    return load_class_map(classes)
