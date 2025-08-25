from fastapi.testclient import TestClient
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

from server.app.main import app
from server.app import engine_service
from engine.world_loader import World, SectionEntry


def test_update_game_state_endpoint():
    engine_service._GAME_STATES.clear()
    engine_service._WORLDS.clear()

    world = World(
        id="w1",
        title="World",
        ruleset="dnd5e",
        end_goal="",
        lore="old",
        locations=[SectionEntry(name="Town", description="")],
        npcs=[],
    )
    engine_service._WORLDS[1] = world
    game_id = engine_service.create_game(1)

    client = TestClient(app)
    resp_w = client.patch("/worlds/1", json={"lore": "new"})
    assert resp_w.status_code == 200

    payload = {
        "party": [{"id": 1, "name": "Hero"}],
        "memory": [{"content": "saved town", "importance": 0.5, "tags": []}],
    }
    resp = client.patch(f"/games/{game_id}", json=payload)
    assert resp.status_code == 200

    state = engine_service.get_game_state(game_id)
    assert state["party"][0]["name"] == "Hero"
    assert state["memory"][0]["content"] == "saved town"
    assert engine_service.get_world(1).lore == "new"
