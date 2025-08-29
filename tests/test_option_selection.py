import asyncio
from pathlib import Path
import sys

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


def test_numeric_option_selection(monkeypatch):
    game_id = _setup_world_and_game()

    async def first_turn(*, model, prompt):
        return "A fork appears.\n1. Go left\n2. Go right"

    monkeypatch.setattr(engine_service, "generate", first_turn)
    asyncio.run(engine_service.run_turn(game_id, "look"))

    captured = {}

    async def second_turn(*, model, prompt):
        captured["prompt"] = prompt
        return "You go right."

    monkeypatch.setattr(engine_service, "generate", second_turn)
    asyncio.run(engine_service.run_turn(game_id, "2"))

    assert "Player: Go right" in captured["prompt"]
    assert "Player: 2" not in captured["prompt"]
