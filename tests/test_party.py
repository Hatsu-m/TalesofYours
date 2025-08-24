import sys
from pathlib import Path

import pytest

sys.path.append(str(Path(__file__).resolve().parents[1]))

from engine import models, context
from engine.world_loader import World, SectionEntry


def _make_world() -> World:
    return World(
        id="w",
        title="World",
        ruleset="dnd5e",
        end_goal="",
        lore="",
        locations=[SectionEntry(name="Town", description="")],
        npcs=[],
        factions=[],
        items=[],
        rules_notes=None,
    )


def test_party_limits_and_prompt_personas() -> None:
    state = models.GameState(
        world_id=1,
        current_location=0,
        party=[],
        flags={},
        timeline=[],
        memory=[],
        pending_roll=None,
    )

    # Add companions up to limit
    for i in range(3):
        state.add_companion({"id": i, "name": f"C{i}", "persona": f"P{i}"})
    with pytest.raises(ValueError):
        state.add_companion({"id": 4, "name": "C4", "persona": "P4"})

    # Add pets up to limit
    for i in range(2):
        state.add_pet({"id": i, "name": f"Pet{i}", "persona": f"PP{i}"})
    with pytest.raises(ValueError):
        state.add_pet({"id": 3, "name": "Pet3", "persona": "PP3"})

    world = _make_world()
    prompt = context.build_prompt(world, state)
    assert "C0: P0" in prompt and "Pet0: PP0" in prompt
