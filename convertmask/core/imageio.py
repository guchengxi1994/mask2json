"""Image IO helpers.

All reads/writes go through ``cv2.imdecode``/``imencode`` on file bytes so
paths with non-ASCII characters work on every platform. Images come back as
RGB (3-channel) arrays; masks as single-channel arrays with their values
preserved (class ids or 0/255).
"""

from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np

from convertmask import SUPPORTED_IMG_EXTS


def read_image(path: Path | str) -> np.ndarray:
    """Read an image as RGB uint8 (grayscale inputs become 3-channel)."""
    raw = np.fromfile(str(path), dtype=np.uint8)
    img = cv2.imdecode(raw, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError(f"cannot read image: {path}")
    return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)


def read_mask(path: Path | str) -> np.ndarray:
    """Read a mask as a 2-D uint8 array, values preserved (no binarization)."""
    raw = np.fromfile(str(path), dtype=np.uint8)
    mask = cv2.imdecode(raw, cv2.IMREAD_GRAYSCALE)
    if mask is None:
        raise ValueError(f"cannot read mask: {path}")
    return mask


def write_image(path: Path | str, img: np.ndarray) -> Path:
    """Write an RGB or grayscale array to disk (creates parent dirs).

    The extension selects the encoder; ``.png`` is lossless and recommended
    for masks.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if img.ndim == 3 and img.shape[2] >= 3:
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    ok, buf = cv2.imencode(path.suffix, img)
    if not ok:
        raise ValueError(f"cannot encode image as {path.suffix}: {path}")
    buf.tofile(str(path))
    return path


def list_images(path: Path | str, recursive: bool = False) -> list[Path]:
    """List supported image files under a file or directory, sorted."""
    path = Path(path)
    if path.is_file():
        return [path]
    if not path.is_dir():
        raise FileNotFoundError(f"not a file or directory: {path}")
    it = path.rglob("*") if recursive else path.glob("*")
    return sorted(p for p in it if p.is_file() and p.suffix.lower() in SUPPORTED_IMG_EXTS)


def image_size(path: Path | str) -> tuple[int, int]:
    """Return ``(width, height)`` of an image."""
    raw = np.fromfile(str(path), dtype=np.uint8)
    img = cv2.imdecode(raw, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError(f"cannot read image: {path}")
    h, w = img.shape[:2]
    return w, h
