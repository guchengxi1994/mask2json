"""Session management for the web server: one temp dir per upload batch."""

from __future__ import annotations

import atexit
import shutil
import tempfile
import uuid
from pathlib import Path


class SessionManager:
    def __init__(self, root: Path | None = None):
        self.root = Path(root) if root else Path(tempfile.mkdtemp(prefix="convertmask-"))
        self.root.mkdir(parents=True, exist_ok=True)
        atexit.register(self.cleanup_all)

    def new(self) -> str:
        sid = uuid.uuid4().hex[:12]
        (self.root / sid).mkdir(parents=True)
        for sub in ("imgs", "labels", "outputs", "analysis"):
            (self.root / sid / sub).mkdir()
        return sid

    def path(self, sid: str) -> Path:
        p = self.root / sid
        if not p.is_dir():
            raise KeyError(f"unknown session {sid}")
        return p

    def resolve(self, sid: str, rel: str) -> Path:
        """Resolve ``rel`` inside the session, rejecting escapes."""
        base = self.path(sid).resolve()
        target = (base / rel).resolve()
        if not str(target).startswith(str(base)):
            raise ValueError("path escapes session directory")
        return target

    def cleanup_all(self) -> None:
        shutil.rmtree(self.root, ignore_errors=True)


sessions = SessionManager()
