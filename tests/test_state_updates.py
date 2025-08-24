import asyncio
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from server.app import engine_service
from engine.world_loader import World, SectionEntry


def _setup_world_and_game() -> int:
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
    return engine_service.create_game(1)


def test_state_update_line(monkeypatch):
    game_id = _setup_world_and_game()
    state = engine_service._GAME_STATES[game_id]
    state.party.append({"id": 1, "name": "Hero", "stats": {"hp": 10}, "inventory": []})

    async def fake_generate(*, model, prompt):
        return (
            "You find a potion and feel healthier.\n"
            "STATE_UPDATE: {\"party\": [{\"id\": 1, \"stats\": {\"hp\": 15},"
            " \"inventory\": {\"add\": [\"Potion\"]}}]}"
        )

    monkeypatch.setattr(engine_service, "generate", fake_generate)

    resp = asyncio.run(engine_service.run_turn(game_id, "search"))

    member = engine_service._GAME_STATES[game_id].party[0]
    assert member["stats"]["hp"] == 15
    assert "Potion" in member["inventory"]
    assert "STATE_UPDATE" not in resp.message
