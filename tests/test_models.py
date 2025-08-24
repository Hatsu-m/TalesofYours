"""CRUD round-trip tests for core models."""

from __future__ import annotations

from pathlib import Path
import sys

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

sys.path.append(str(Path(__file__).resolve().parents[1]))

from engine import models
from server import schemas


def test_gamestate_round_trip() -> None:
    engine = create_engine("sqlite:///:memory:", future=True)
    models.Base.metadata.create_all(engine)

    with Session(engine) as session:
        world = models.WorldMeta(title="Test World", ruleset="dnd5e")
        session.add(world)
        session.flush()

        location = models.Location(world_id=world.id, name="Town Square")
        session.add(location)
        session.flush()

        hero = models.Character(
            name="Hero", stats=models.Stats(hp=10, strength=5).model_dump()
        )
        session.add(hero)
        session.flush()

        state = models.GameState(
            world_id=world.id,
            current_location=location.id,
            party=[{"id": hero.id, "name": hero.name}],
            flags={"intro": True},
            timeline=[],
            memory=[],
            pending_roll=None,
        )
        session.add(state)
        session.commit()
        state_id = state.id
        world_id = world.id

    with Session(engine) as session:
        loaded = session.get(models.GameState, state_id)
        assert loaded is not None
        schema_state = schemas.GameState.model_validate(loaded, from_attributes=True)

        assert schema_state.world_id == world_id
        assert schema_state.flags["intro"] is True
        assert schema_state.party[0]["name"] == "Hero"
