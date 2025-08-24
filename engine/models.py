"""Core game data models."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel
from sqlalchemy import ForeignKey, JSON, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base declarative class for all models."""


class Stats(BaseModel):
    """Basic character statistics."""

    hp: int = 0
    strength: int = 0
    defense: int = 0


class WorldMeta(Base):
    """Metadata about a world."""

    __tablename__ = "world_meta"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    ruleset: Mapped[str] = mapped_column(String, nullable=False)


class Location(Base):
    """A location within a world."""

    __tablename__ = "locations"

    id: Mapped[int] = mapped_column(primary_key=True)
    world_id: Mapped[int] = mapped_column(ForeignKey("world_meta.id"), nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String, nullable=True)


class NPC(Base):
    """Non-player character."""

    __tablename__ = "npcs"

    id: Mapped[int] = mapped_column(primary_key=True)
    world_id: Mapped[int] = mapped_column(ForeignKey("world_meta.id"), nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    role: Mapped[Optional[str]] = mapped_column(String, nullable=True)


class Item(Base):
    """Game item."""

    __tablename__ = "items"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String, nullable=True)


class Quest(Base):
    """Quest definition."""

    __tablename__ = "quests"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String, nullable=True)


class Character(Base):
    """Base character model supporting single table inheritance."""

    __tablename__ = "characters"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    stats: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    type: Mapped[str] = mapped_column(String(50), default="character")

    __mapper_args__ = {"polymorphic_on": type, "polymorphic_identity": "character"}


class Companion(Character):
    """Companion character."""

    __mapper_args__ = {"polymorphic_identity": "companion"}


class Pet(Character):
    """Pet character."""

    __mapper_args__ = {"polymorphic_identity": "pet"}


class RuleConfig(Base):
    """Configuration for rulesets."""

    __tablename__ = "rule_configs"

    id: Mapped[int] = mapped_column(primary_key=True)
    ruleset: Mapped[str] = mapped_column(String, nullable=False)


class GameState(Base):
    """Persisted state of an ongoing game."""

    __tablename__ = "game_states"

    id: Mapped[int] = mapped_column(primary_key=True)
    world_id: Mapped[int] = mapped_column(ForeignKey("world_meta.id"), nullable=False)
    current_location: Mapped[int] = mapped_column(
        ForeignKey("locations.id"), nullable=False
    )
    party: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=list)
    flags: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    timeline: Mapped[List[str]] = mapped_column(JSON, default=list)
    memory: Mapped[List[str]] = mapped_column(JSON, default=list)
    pending_roll: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
