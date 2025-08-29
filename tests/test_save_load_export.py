import asyncio

from fastapi.testclient import TestClient

from server.app import engine_service
from server.app.main import app
from engine.world_loader import World, SectionEntry, load_world


def test_save_export_import_flow(tmp_path, monkeypatch):
    """Game state can be saved, exported, imported and resumed."""

    # Prepare a simple world and game state
    world = World(
        id="w1",
        title="World",
        ruleset="dnd5e",
        end_goal="",
        lore="lore",
        locations=[SectionEntry(name="Start", description="desc")],
        npcs=[],
    )
    engine_service._WORLDS[1] = world
    state = engine_service.GameState(world_id=1, current_location=0)
    state.pending_roll = {"id": "abc", "dc": 10}
    engine_service._GAME_STATES[1] = state

    client = TestClient(app)

    # Save the game to disk
    engine_service.SAVE_DIR = tmp_path
    resp = client.post("/games/1/save")
    assert resp.status_code == 200
    save_path = tmp_path / "game_1.json"
    assert save_path.exists()

    # Export the saved game
    resp = client.get("/games/1/export")
    assert resp.status_code == 200
    saved = resp.json()
    assert saved["pending_roll"]["dc"] == 10

    # Export the world
    resp_w = client.get("/worlds/1/export")
    assert resp_w.status_code == 200
    md_text = resp_w.text
    assert "id: w1" in md_text

    # Wipe in-memory storage
    engine_service._GAME_STATES.clear()
    engine_service._WORLDS.clear()

    # Re-import world from exported markdown
    path = tmp_path / "world.md"
    path.write_text(md_text)
    engine_service._WORLDS[1] = load_world(path)

    # Import game state
    resp_import = client.post("/games/import", json={"state": saved})
    assert resp_import.status_code == 200
    new_id = resp_import.json()["id"]
    assert new_id == 1
    assert engine_service._GAME_STATES[new_id].pending_roll == saved["pending_roll"]

    # Resume play
    async def fake_generate(*, model, prompt):
        return "Resumed."

    monkeypatch.setattr(engine_service, "generate", fake_generate)
    result = asyncio.run(engine_service.run_turn(new_id, "hello"))
    assert result.message == "Resumed."
    assert engine_service._GAME_STATES[new_id].pending_roll is None
