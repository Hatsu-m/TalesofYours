from pathlib import Path
import sys

from fastapi.testclient import TestClient

sys.path.append(str(Path(__file__).resolve().parents[1]))

from server.app.main import app
from server.app import engine_service
from engine.world_loader import World, SectionEntry


def setup_world():
    engine_service._GAME_STATES.clear()
    engine_service._WORLDS.clear()
    world = World(
        id="w1",
        title="World",
        ruleset="simple_d20",
        stats=["tech", "firearms"],
        end_goal="",
        lore="",
        locations=[SectionEntry(name="Town", description="")],
        npcs=[],
    )
    engine_service._WORLDS[1] = world
    return engine_service.create_game(1)


def test_stat_name_restriction():
    game_id = setup_world()
    client = TestClient(app)
    payload = {"party": [{"id": 1, "name": "Hero", "stats": {"hp": 10, "tech": 3}}]}
    assert client.patch(f"/games/{game_id}", json=payload).status_code == 200

    bad_payload = {
        "party": [{"id": 1, "name": "Hero", "stats": {"hp": 10, "strength": 1}}]
    }
    resp = client.patch(f"/games/{game_id}", json=bad_payload)
    assert resp.status_code == 400


def test_stat_value_cap():
    game_id = setup_world()
    client = TestClient(app)
    payload = {"party": [{"id": 1, "name": "Hero", "stats": {"hp": 10, "tech": 7}}]}
    resp = client.patch(f"/games/{game_id}", json=payload)
    assert resp.status_code == 400
