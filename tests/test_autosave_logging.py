import asyncio
import json
import sys
from pathlib import Path

from fastapi.testclient import TestClient

sys.path.append(str(Path(__file__).resolve().parents[1]))

from server.app import engine_service
from server.app.main import app
from engine.world_loader import World, SectionEntry


def _setup_world_and_game(tmp_path: Path) -> int:
    engine_service.SAVE_DIR = tmp_path
    world = World(
        id="w",
        title="World",
        ruleset="dnd5e",
        end_goal="",
        lore="",
        locations=[SectionEntry(name="Start", description="")],
        npcs=[],
    )
    engine_service._WORLDS[1] = world
    game_id = engine_service.create_game(1)
    return game_id


def test_transcript_and_autosave(tmp_path, monkeypatch):
    game_id = _setup_world_and_game(tmp_path)

    async def fake_generate(*, model, prompt):
        return "DM reply"

    monkeypatch.setattr(engine_service, "generate", fake_generate)

    state = engine_service._GAME_STATES[game_id]
    state.flags["score"] = 7

    asyncio.run(engine_service.run_turn(game_id, "hello"))

    transcript = tmp_path / f"game_{game_id}.jsonl"
    autosave = tmp_path / f"game_{game_id}.json"

    assert transcript.exists() and autosave.exists()

    lines = [json.loads(line) for line in transcript.read_text().splitlines()]
    assert lines[0] == {"actor": "player", "text": "hello"}
    assert lines[1]["actor"] == "dm"

    history = engine_service.read_transcript(game_id)
    assert history[0] == {"actor": "player", "text": "hello"}

    client = TestClient(app)
    resp_hist = client.get(f"/games/{game_id}/transcript")
    assert resp_hist.status_code == 200
    assert resp_hist.json()[0] == {"actor": "player", "text": "hello"}

    data = json.loads(autosave.read_text())
    assert data["flags"]["score"] == 7

    engine_service._GAME_STATES.clear()
    engine_service.load_autosave(game_id)
    restored = engine_service._GAME_STATES[game_id]
    assert restored.flags["score"] == 7
