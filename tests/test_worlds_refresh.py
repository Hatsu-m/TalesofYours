from fastapi.testclient import TestClient

from server.app import engine_service
from server.app.main import app


def test_world_listing_detects_new_files() -> None:
    client = TestClient(app)
    initial = client.get("/worlds").json()
    path = engine_service.WORLD_DIR / "temp_world.md"
    content = (
        "---\n"
        "id: temp\n"
        "title: Temp World\n"
        "ruleset: custom_d6\n"
        "end_goal: fun\n"
        "---\n\n"
        "## Lore\n"
        "Temporary world\n"
    )
    path.write_text(content, encoding="utf-8")
    try:
        updated = client.get("/worlds").json()
        assert len(updated) == len(initial) + 1
    finally:
        if path.exists():
            path.unlink()
        wid = engine_service._WORLD_FILES.pop(path, None)
        if wid is not None:
            engine_service._WORLDS.pop(wid, None)
