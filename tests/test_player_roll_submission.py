"""Integration test for player roll submission endpoint."""

from pathlib import Path
import sys
import asyncio

sys.path.append(str(Path(__file__).resolve().parents[1]))

from fastapi.testclient import TestClient

from server.app import engine_service
from server.app.main import app
from engine.world_loader import World, SectionEntry


def test_player_roll_submission(monkeypatch):
    responses = [
        "You look around. Roll a d20 for Perception (DC 10).",
        "You spot a hidden door.",
    ]

    async def fake_generate(*, model, prompt):
        return responses.pop(0)

    monkeypatch.setattr(engine_service, "generate", fake_generate)

    world = World(
        id="w1",
        title="World",
        ruleset="dnd5e",
        end_goal="",
        lore="",
        locations=[SectionEntry(name="Start", description="")],
        npcs=[],
    )
    engine_service._WORLDS[1] = world
    engine_service._GAME_STATES[1] = engine_service.GameState(
        world_id=1, current_location=0
    )

    asyncio.run(engine_service.run_turn(1, "look"))

    pending = engine_service._GAME_STATES[1].pending_roll
    assert pending is not None

    client = TestClient(app)
    resp = client.post(
        "/games/1/player-roll",
        json={"request_id": pending["id"], "value": 15, "mod": 0},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["awaiting_player_roll"] is False
    assert data["message"] == "You spot a hidden door."
    assert engine_service._GAME_STATES[1].pending_roll is None
