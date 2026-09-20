"""FastAPI application: upload, convert, augment, analyze, file serving."""

from __future__ import annotations

import io
import logging
import zipfile
from pathlib import Path
from typing import Annotated

from fastapi import FastAPI, HTTPException, Query, UploadFile
from fastapi.params import File
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles

from convertmask import SUPPORTED_CLASSFILE_EXTS, SUPPORTED_IMG_EXTS
from convertmask.converters import CONVERTER_ARGS, convert
from convertmask.server.sessions import sessions

logger = logging.getLogger("convertmask.server")

_STATIC_DIR = Path(__file__).parent / "static"


def create_app() -> FastAPI:
    app = FastAPI(title="convertmask", version="1.0.0")
    _register_routes(app)
    if _STATIC_DIR.is_dir():
        app.mount("/", StaticFiles(directory=_STATIC_DIR, html=True), name="static")
    return app


def _resolve_or_400(sid: str, rel: str) -> Path:
    """Session-relative path resolution with escapes rejected as 400."""
    try:
        return sessions.resolve(sid, rel)
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc


def _register_routes(app: FastAPI) -> None:
    @app.post("/api/session")
    def new_session():
        return {"session": sessions.new()}

    @app.post("/api/upload/{sid}")
    async def upload(
        sid: str,
        as_: Annotated[str, Query(alias="as")] = "",
        files: Annotated[list[UploadFile], File()] = None,
    ):
        """Store uploaded files; ``?as=mask`` routes images into ``masks/``."""
        base = sessions.path(sid)
        as_mask = as_ == "mask"
        stored = {"images": [], "masks": [], "labels": [], "classes": []}
        for f in files or []:
            name = Path(f.filename or "file").name
            suffix = Path(name).suffix.lower()
            data = await f.read()

            if suffix in SUPPORTED_IMG_EXTS:
                sub, key = ("masks", "masks") if as_mask else ("imgs", "images")
                dest = base / sub / name
            elif suffix in {".json", ".xml"}:
                dest, key = base / "labels" / name, "labels"
            elif suffix == ".txt":
                if _looks_like_yolo_labels(data):
                    dest, key = base / "labels" / name, "labels"
                else:
                    dest, key = base / name, "classes"
            elif suffix in {".yaml", ".yml", ".names"}:
                dest, key = base / name, "classes"
            else:
                continue
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(data)
            stored[key].append(name)
        return stored

    @app.get("/api/files/{sid}")
    def list_files(sid: str):
        base = sessions.path(sid)

        def walk(sub: str) -> list[str]:
            d = base / sub
            if not d.is_dir():
                return []
            return sorted(
                str(p.relative_to(base)) for p in d.rglob("*") if p.is_file()
            )

        return {
            "images": walk("imgs"),
            "masks": walk("masks"),
            "labels": walk("labels"),
            "classes": [
                p.name for p in base.iterdir()
                if p.is_file() and p.suffix.lower() in SUPPORTED_CLASSFILE_EXTS
            ],
            "outputs": walk("outputs"),
            "analysis": walk("analysis"),
        }

    @app.post("/api/convert/{sid}")
    def api_convert(sid: str, body: dict):
        method = body.get("method", "")
        base = sessions.path(sid)
        allowed = CONVERTER_ARGS.get(_norm(method), [])
        kwargs: dict[str, Path] = {}
        for name in allowed:
            value = body.get(name)
            if value is None:
                continue
            p = _resolve_or_400(sid, str(value))
            if not p.exists():
                raise HTTPException(400, f"{name}: {value} not found in session")
            kwargs[name] = p
        if "out" in allowed:
            kwargs.setdefault("out", base / "outputs")
        try:
            outputs = convert(method, **kwargs)
        except (ValueError, FileNotFoundError, TypeError) as exc:
            raise HTTPException(400, str(exc)) from exc
        return {"outputs": [str(p.relative_to(base)) for p in outputs]}

    @app.post("/api/augment/{sid}")
    def api_augment(sid: str, body: dict):
        from convertmask.augment import augment_images

        base = sessions.path(sid)
        imgs = _resolve_or_400(sid, str(body.get("imgs", "imgs")))
        labels = body.get("labels")
        if labels:
            labels = _resolve_or_400(sid, str(labels))
        methods = body.get("methods") or None
        if isinstance(methods, str):
            methods = [m.strip() for m in methods.split(",") if m.strip()]
        try:
            outputs = augment_images(
                imgs=imgs,
                labels=labels,
                methods=methods,
                number=int(body.get("number", 1)),
                seed=body.get("seed"),
                out=base / "outputs",
                label_fmt=body.get("label_fmt"),
                save_mask=bool(body.get("save_mask", False)),
            )
        except (ValueError, FileNotFoundError, TypeError) as exc:
            raise HTTPException(400, str(exc)) from exc
        return {"outputs": [str(p.relative_to(base)) for p in outputs]}

    @app.post("/api/analyze/{sid}")
    def api_analyze(sid: str, body: dict):
        from convertmask.analyze import analyze_dataset

        base = sessions.path(sid)
        annos = _resolve_or_400(sid, str(body.get("annos", "labels")))
        imgs = body.get("imgs")
        if imgs:
            imgs = _resolve_or_400(sid, str(imgs))
        classes = body.get("classes")
        if classes:
            classes = _resolve_or_400(sid, str(classes))
        baseline = body.get("baseline")
        if baseline:
            baseline = _resolve_or_400(sid, str(baseline))
        try:
            report = analyze_dataset(
                annos=annos, imgs=imgs, classes=classes,
                out=base / "analysis", baseline=baseline,
            )
        except (ValueError, FileNotFoundError) as exc:
            raise HTTPException(400, str(exc)) from exc
        return report

    @app.get("/api/file/{sid}")
    def serve_file(sid: str, path: str):
        p = _resolve_or_400(sid, path)
        if not p.is_file():
            raise HTTPException(404, "not found")
        return FileResponse(p)

    @app.get("/api/download/{sid}")
    def download(sid: str, which: str = "outputs"):
        base = sessions.path(sid)
        target = base / which
        if not target.is_dir() or not any(target.rglob("*")):
            raise HTTPException(404, f"nothing to download in {which}/")
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
            for p in sorted(target.rglob("*")):
                if p.is_file():
                    zf.write(p, p.relative_to(base))
        buf.seek(0)
        return StreamingResponse(
            buf,
            media_type="application/zip",
            headers={"Content-Disposition": f'attachment; filename="{which}.zip"'},
        )

    @app.get("/api/health")
    def health():
        return {"status": "ok"}


def _norm(method: str) -> str:
    from convertmask.converters import normalize_method

    try:
        return normalize_method(method)
    except ValueError:
        return ""


def _looks_like_yolo_labels(data: bytes) -> bool:
    """Distinguish YOLO label txts from class-name txts by their first line.

    A label line is ``<int> <float> <float> <float> <float>``; a class file
    line is a bare name.
    """
    try:
        text = data.decode("utf-8", errors="replace")
    except Exception:  # pragma: no cover - decode with replace never raises
        return False
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        parts = line.split()
        if len(parts) == 5 and parts[0].lstrip("-").isdigit():
            try:
                float(parts[1]), float(parts[2]), float(parts[3]), float(parts[4])
                return True
            except ValueError:
                return False
        return False
    return False
