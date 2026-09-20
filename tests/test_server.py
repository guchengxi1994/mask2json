"""Web server integration tests via fastapi TestClient."""

from __future__ import annotations

import io

import cv2
import numpy as np
import pytest
from fastapi.testclient import TestClient

from convertmask.server.app import create_app
from tests.conftest import make_image, make_mask


@pytest.fixture
def client(tmp_path, monkeypatch):
    from convertmask.server import sessions as sessions_mod

    manager = sessions_mod.SessionManager(root=tmp_path / "sessions")
    monkeypatch.setattr(sessions_mod, "sessions", manager)
    # the routes close over the module-level `sessions`, so rebuild the app
    import convertmask.server.app as app_mod

    monkeypatch.setattr(app_mod, "sessions", manager)
    app = create_app()
    return TestClient(app)


def _jpg_bytes(arr: np.ndarray) -> bytes:
    ok, buf = cv2.imencode(".jpg", arr[..., ::-1])
    assert ok
    return buf.tobytes()


def _png_bytes(arr: np.ndarray) -> bytes:
    ok, buf = cv2.imencode(".png", arr)
    assert ok
    return buf.tobytes()


def _upload(client: TestClient, sid: str, files: list[tuple[str, str, bytes]], as_mask=False):
    files_arg = [("files", (name, io.BytesIO(data), "application/octet-stream"))
                 for name, _, data in files]
    r = client.post(f"/api/upload/{sid}" + ("?as=mask" if as_mask else ""), files=files_arg)
    assert r.status_code == 200, r.text
    return r.json()


def test_health(client):
    assert client.get("/api/health").json() == {"status": "ok"}


def test_full_flow_convert_augment_analyze(client):
    # 1. session + upload images / masks / classes
    sid = client.post("/api/session").json()["session"]
    res = _upload(client, sid, [
        ("a.jpg", "img", _jpg_bytes(make_image())),
    ])
    assert res["images"] == ["a.jpg"]
    res = _upload(client, sid, [
        ("a.png", "mask", _png_bytes(make_mask())),
    ], as_mask=True)
    assert res["masks"] == ["a.jpg".replace("jpg", "png")][:1] or res["masks"] == ["a.png"]
    _upload(client, sid, [("classes.txt", "c", b"cat\ndog\n")])

    files = client.get(f"/api/files/{sid}").json()
    assert files["images"] == ["imgs/a.jpg"]
    assert files["masks"] == ["masks/a.png"]
    assert files["classes"] == ["classes.txt"]

    # 2. convert mask2json
    r = client.post(f"/api/convert/{sid}", json={
        "method": "mask2json", "imgs": "imgs", "masks": "masks",
        "classes": "classes.txt",
    })
    assert r.status_code == 200, r.text
    outputs = r.json()["outputs"]
    assert any(o.endswith("a.json") for o in outputs)

    # 3. augment (labels = the converted jsons now in outputs)
    files = client.get(f"/api/files/{sid}").json()
    r = client.post(f"/api/augment/{sid}", json={
        "imgs": "imgs", "labels": "outputs", "methods": ["noise", "translation"],
        "number": 1, "seed": 11,
    })
    assert r.status_code == 200, r.text
    assert any(o.endswith(".xml") or o.endswith(".json") for o in r.json()["outputs"])

    # 4. analyze the labelme jsons
    r = client.post(f"/api/analyze/{sid}", json={"annos": "outputs", "imgs": "imgs"})
    assert r.status_code == 200, r.text
    report = r.json()
    assert report["summary"]["annotations"] >= 1
    assert "class_distribution" in report["summary"]

    # 5. download zips
    r = client.get(f"/api/download/{sid}?which=analysis")
    assert r.status_code == 200 and r.headers["content-type"] == "application/zip"


def test_upload_txt_classification(client):
    sid = client.post("/api/session").json()["session"]
    res = _upload(client, sid, [
        ("yolo.txt", "y", b"0 0.5 0.5 0.2 0.2\n"),
        ("names.txt", "n", b"cat\ndog\n"),
        ("info.yaml", "y", b"label_names:\n  cat: 1\n"),
    ])
    assert res["labels"] == ["yolo.txt"]
    assert set(res["classes"]) == {"names.txt", "info.yaml"}


def test_path_escape_rejected(client):
    sid = client.post("/api/session").json()["session"]
    r = client.get(f"/api/file/{sid}", params={"path": "../../etc/passwd"})
    assert r.status_code in (400, 404, 500)  # rejected, never serves outside


def test_convert_bad_method_400(client):
    sid = client.post("/api/session").json()["session"]
    r = client.post(f"/api/convert/{sid}", json={"method": "zzz"})
    assert r.status_code == 400


def test_static_index_served(client):
    r = client.get("/")
    assert r.status_code == 200
    assert b"convertmask" in r.content
