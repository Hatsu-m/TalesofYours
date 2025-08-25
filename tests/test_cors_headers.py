from pathlib import Path
import sys

from fastapi.testclient import TestClient

sys.path.append(str(Path(__file__).resolve().parents[1]))

from server.app.main import app


def test_cors_headers_present():
    client = TestClient(app)
    resp = client.get("/worlds", headers={"Origin": "http://localhost:5173"})
    assert resp.headers.get("access-control-allow-origin") == "*"
