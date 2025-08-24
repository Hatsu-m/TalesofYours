import asyncio
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

from server.app import engine_service
from engine.world_loader import World


def _make_world(idx: int, ruleset: str) -> None:
    world = World(
        id=f"w{idx}",
        title="World",
        ruleset=ruleset,
        end_goal="",
        lore="",
        locations=[],
        npcs=[],
    )
    engine_service._WORLDS[idx] = world


def test_submit_roll_uses_world_rules(monkeypatch):
    _make_world(1, "dnd5e")
    _make_world(2, "custom_d6")
    game_dnd = engine_service.create_game(1)
    game_d6 = engine_service.create_game(2)
    engine_service._GAME_STATES[game_dnd].pending_roll = {"id": "a", "dc": 10}
    engine_service._GAME_STATES[game_d6].pending_roll = {"id": "b", "dc": 4}

    async def fake_generate(*, model, prompt):
        return "narration"

    monkeypatch.setattr(engine_service, "generate", fake_generate)

    asyncio.run(engine_service.submit_player_roll(game_dnd, "a", 6, 0))
    asyncio.run(engine_service.submit_player_roll(game_d6, "b", 6, 0))

    mem_dnd = engine_service._GAME_STATES[game_dnd].memory[0].content
    mem_d6 = engine_service._GAME_STATES[game_d6].memory[0].content
    assert "failure" in mem_dnd
    assert "success" in mem_d6
