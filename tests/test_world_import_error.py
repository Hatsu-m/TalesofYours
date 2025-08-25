from fastapi.testclient import TestClient

from server.app.main import app


def test_import_invalid_world_returns_400():
    client = TestClient(app)
    invalid_md = "---\n---\n"  # Missing required fields
    response = client.post("/worlds/import", json={"content": invalid_md})
    assert response.status_code == 400
