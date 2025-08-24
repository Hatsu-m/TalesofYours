from pathlib import Path
import sys

from fastapi.testclient import TestClient

sys.path.append(str(Path(__file__).resolve().parents[1]))

from server.app.main import app


def test_openapi_has_public_routes():
    client = TestClient(app)
    paths = client.get("/openapi.json").json()["paths"]
    expected = [
        "/worlds",
        "/worlds/{world_id}",
        "/worlds/import",
        "/worlds/{world_id}/export",
        "/games",
        "/games/{game_id}",
        "/games/{game_id}/turn",
        "/games/{game_id}/player-roll",
        "/games/{game_id}/companions",
        "/games/{game_id}/companions/{companion_id}",
        "/games/{game_id}/save",
        "/games/import",
        "/health",
        "/health/llm",
    ]
    for path in expected:
        assert path in paths
