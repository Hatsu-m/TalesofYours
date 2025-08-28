import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from server.app import engine_service
from engine.world_loader import World, SectionEntry


def _setup_world() -> int:
    engine_service._GAME_STATES.clear()
    engine_service._WORLDS.clear()
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


def test_thirst_drops_faster(monkeypatch):
    game_id = _setup_world()
    state = engine_service._GAME_STATES[game_id]
    state.party.append({"id": 1, "name": "Hero", "stats": {"hp": 10}})
    monkeypatch.setattr(engine_service, "HUNGER_DECAY_SECONDS", 2)
    monkeypatch.setattr(engine_service, "THIRST_DECAY_SECONDS", 1)
    engine_service.advance_time(game_id, 4)
    member = engine_service._GAME_STATES[game_id].party[0]
    assert member["stats"]["hunger"] == 8
    assert member["stats"]["thirst"] == 6


def test_damage_when_needs_empty(monkeypatch):
    game_id = _setup_world()
    state = engine_service._GAME_STATES[game_id]
    state.party.append(
        {"id": 1, "name": "Hero", "stats": {"hp": 10, "hunger": 0, "thirst": 0}}
    )
    monkeypatch.setattr(engine_service, "HUNGER_DECAY_SECONDS", 1)
    monkeypatch.setattr(engine_service, "THIRST_DECAY_SECONDS", 1)
    engine_service.advance_time(game_id, 3)
    member = engine_service._GAME_STATES[game_id].party[0]
    assert member["stats"]["hp"] == 4


def test_eat_and_drink_restore():
    game_id = _setup_world()
    state = engine_service._GAME_STATES[game_id]
    state.party.append(
        {"id": 1, "name": "Hero", "stats": {"hp": 10, "hunger": 3, "thirst": 2}}
    )
    engine_service.feed_member(game_id, 1)
    engine_service.hydrate_member(game_id, 1)
    member = engine_service._GAME_STATES[game_id].party[0]
    assert member["stats"]["hunger"] == engine_service.MAX_HUNGER
    assert member["stats"]["thirst"] == engine_service.MAX_THIRST
