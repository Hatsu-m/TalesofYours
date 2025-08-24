"""Pydantic schemas mirroring core models."""

from __future__ import annotations

from typing import Any, Dict, List

from pydantic import BaseModel, ConfigDict


class Stats(BaseModel):
    hp: int = 0
    strength: int = 0
    defense: int = 0


class WorldMeta(BaseModel):
    id: int | None = None
    title: str
    ruleset: str

    model_config = ConfigDict(from_attributes=True)


class Location(BaseModel):
    id: int | None = None
    world_id: int
    name: str
    description: str | None = None

    model_config = ConfigDict(from_attributes=True)


class NPC(BaseModel):
    id: int | None = None
    world_id: int
    name: str
    role: str | None = None

    model_config = ConfigDict(from_attributes=True)


class Item(BaseModel):
    id: int | None = None
    name: str
    description: str | None = None

    model_config = ConfigDict(from_attributes=True)


class Quest(BaseModel):
    id: int | None = None
    title: str
    description: str | None = None

    model_config = ConfigDict(from_attributes=True)


class Character(BaseModel):
    id: int | None = None
    name: str
    stats: Stats

    model_config = ConfigDict(from_attributes=True)


class Companion(Character):
    pass


class Pet(Character):
    pass


class RuleConfig(BaseModel):
    id: int | None = None
    ruleset: str

    model_config = ConfigDict(from_attributes=True)


class GameState(BaseModel):
    id: int | None = None
    world_id: int
    current_location: int
    party: List[Dict[str, Any]]
    flags: Dict[str, Any]
    timeline: List[str]
    memory: List[str]
    pending_roll: Dict[str, Any] | None = None

    model_config = ConfigDict(from_attributes=True)
