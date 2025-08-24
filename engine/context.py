"""Prompt building utilities for the game engine."""

from __future__ import annotations

from typing import List

from .memory import recall
from .world_loader import SectionEntry, World


def _format_entries(entries: List[SectionEntry]) -> str:
    return ", ".join(entry.name for entry in entries) if entries else "none"


def build_prompt(world: World, state: object, k: int = 5) -> str:
    """Build a textual prompt for the LLM based on the game state.

    Parameters
    ----------
    world:
        The current world definition.
    state:
        An object with ``current_location``, ``party``, ``memory`` and
        ``pending_roll`` attributes.
    k:
        Number of memories to include.
    """

    parts: List[str] = []

    # Location description
    try:
        location = world.locations[state.current_location]
        parts.append(f"Location: {location.name} - {location.description}")
    except (IndexError, AttributeError):
        parts.append("Location: unknown")

    # NPCs
    npcs = _format_entries(world.npcs)
    parts.append(f"NPCs here: {npcs}")

    # Party roster
    party_names = ", ".join(
        member.get("name", "?") for member in getattr(state, "party", [])
    )
    parts.append(f"Party: {party_names or 'none'}")

    # Memories
    memories = getattr(state, "memory", [])
    top = recall(memories, k)
    if top:
        parts.append("Memories: " + "; ".join(m.content for m in top))

    # Rules highlights
    if world.rules_notes:
        parts.append(f"Rules: {world.rules_notes}")

    # Pending roll guard
    if getattr(state, "pending_roll", None):
        parts.append("Awaiting player roll — do not resolve.")

    return "\n".join(parts)
