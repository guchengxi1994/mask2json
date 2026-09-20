"""Base64 embedding of images for labelme JSON ``imageData``."""

from __future__ import annotations

import base64
from pathlib import Path

import cv2
import numpy as np


def encode_image(source: Path | str | np.ndarray) -> str:
    """Base64 string of a PNG encoding of the image.

    Accepts an image file path (any format; re-encoded to PNG for
    consistency) or an RGB/grayscale ndarray.
    """
    if isinstance(source, np.ndarray):
        img = source
        if img.ndim == 3 and img.shape[2] >= 3:
            img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        ok, buf = cv2.imencode(".png", img)
        if not ok:
            raise ValueError("cannot encode array to PNG")
        return base64.b64encode(buf.tobytes()).decode("ascii")
    path = Path(source)
    img = cv2.imdecode(np.fromfile(str(path), dtype=np.uint8), cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError(f"cannot read image: {path}")
    ok, buf = cv2.imencode(".png", img)
    if not ok:
        raise ValueError(f"cannot encode {path} to PNG")
    return base64.b64encode(buf.tobytes()).decode("ascii")


def decode_to_array(data: str | None) -> np.ndarray | None:
    """Decode labelme ``imageData`` into an RGB array (None if absent)."""
    if not data:
        return None
    raw = np.frombuffer(base64.b64decode(data), dtype=np.uint8)
    img = cv2.imdecode(raw, cv2.IMREAD_COLOR)
    if img is None:
        return None
    return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
