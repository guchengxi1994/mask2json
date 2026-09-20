"""Class-file handling (txt list or labelme ``info.yaml`` name->id map)."""

from __future__ import annotations

from pathlib import Path

import yaml


def load_class_map(path: Path | str) -> dict[str, int]:
    """Read a class file into ``{class_name: id}``.

    - ``.txt``: one class name per line; ids are 1..N in file order.
    - ``.yaml``/``.yml``: ``label_names`` mapping (with or without an
      explicit ``_background_: 0`` entry), like labelme ``info.yaml``.
    """
    path = Path(path)
    if path.suffix.lower() in {".yaml", ".yml"}:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        if isinstance(data, dict) and "label_names" in data:
            data = data["label_names"]
        if not isinstance(data, dict):
            raise ValueError(f"{path}: expected a label_names mapping, got {type(data).__name__}")
        mapping = {str(k): int(v) for k, v in data.items()}
    else:
        names = [
            line.strip()
            for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        if len(set(names)) != len(names):
            raise ValueError(f"{path}: duplicate class names")
        mapping = {name: i + 1 for i, name in enumerate(names)}
    mapping.pop("_background_", None)
    return mapping


def save_class_map(path: Path | str, mapping: dict[str, int]) -> Path:
    """Write a labelme-style ``info.yaml`` (``_background_`` forced to 0)."""
    path = Path(path)
    full = {"_background_": 0, **{str(k): int(v) for k, v in mapping.items()}}
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        yaml.safe_dump({"label_names": full}, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )
    return path


def class_map_from_names(names: list[str]) -> dict[str, int]:
    """Assign ids 1..N in first-appearance order (background = 0 implied)."""
    seen: list[str] = []
    for n in names:
        if n and n not in seen:
            seen.append(n)
    return {name: i + 1 for i, name in enumerate(seen)}
