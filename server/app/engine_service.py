"""Turn orchestration service for the game engine."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Any, Dict

from engine.context import build_prompt
from engine.memory import MemoryItem, remember
from engine.world_loader import World

from .llm.ollama_client import generate


# In-memory storage used as a temporary stand‑in for a database.  The
# surrounding application will eventually replace this with proper
# persistence but for now it allows ``run_turn`` to function in tests and
# examples without additional infrastructure.
_GAME_STATES: dict[int, "GameState"] = {}
_WORLDS: dict[int, World] = {}


@dataclass
class GameState:
    """Minimal game state container used for turn processing."""

    world_id: int
    current_location: int
    party: list[dict[str, Any]] = field(default_factory=list)
    flags: dict[str, Any] = field(default_factory=dict)
    timeline: list[str] = field(default_factory=list)
    memory: list[MemoryItem] = field(default_factory=list)
    pending_roll: Dict[str, Any] | None = None


@dataclass
class DMResponse:
    """Response returned after processing a turn."""

    message: str
    awaiting_player_roll: bool = False
    roll_request: Dict[str, Any] | None = None


SYSTEM_INSTRUCTIONS = (
    "You are a fair and impartial DM. "
    "Describe the world and the results of actions, "
    "but never roll for the player."
)


async def run_turn(
    game_id: int, player_message: str, *, model: str = "llama3"
) -> DMResponse:
    """Run a single game turn and return the DM's response.

    Parameters
    ----------
    game_id:
        Identifier of the game state to operate on.
    player_message:
        The latest message supplied by the player.
    model:
        Ollama model tag to use for generation.
    """

    state = _GAME_STATES.get(game_id)
    if state is None:
        raise KeyError(f"Unknown game id: {game_id}")

    world = _WORLDS.get(state.world_id)
    if world is None:
        raise KeyError(f"Unknown world id: {state.world_id}")

    # Assemble the prompt for the LLM.
    prompt_context = build_prompt(world, state)
    prompt = (
        f"{SYSTEM_INSTRUCTIONS}\n{prompt_context}\n" f"Player: {player_message}\nDM:"
    )

    narration = await generate(model=model, prompt=prompt)

    # Attempt to detect roll requests.  This module is introduced in a
    # later phase of development, so we fail gracefully if it is missing.
    try:  # pragma: no cover - simple optional dependency shim
        from engine.mechanics import detect_roll_request
    except Exception:  # pragma: no cover - executed only when module absent

        def detect_roll_request(_: str) -> Dict[str, Any] | None:
            return None

    roll_request_obj = detect_roll_request(narration)
    if roll_request_obj:
        roll_request = roll_request_obj.model_dump()
        roll_request["id"] = str(uuid.uuid4())
        awaiting_player_roll = True
    else:
        roll_request = None
        awaiting_player_roll = False
    state.pending_roll = roll_request

    # Store narration in long‑term memory.
    remember(state.memory, narration)

    # Persist the updated state.
    _GAME_STATES[game_id] = state

    return DMResponse(
        message=narration,
        awaiting_player_roll=awaiting_player_roll,
        roll_request=roll_request,
    )


async def submit_player_roll(
    game_id: int,
    request_id: str,
    value: int,
    mod: int = 0,
    *,
    model: str = "llama3",
) -> DMResponse:
    """Resolve a player-supplied roll and return the DM's narration."""

    state = _GAME_STATES.get(game_id)
    if state is None:
        raise KeyError(f"Unknown game id: {game_id}")
    pending = state.pending_roll
    if not pending or pending.get("id") != request_id:
        raise ValueError("No matching pending roll")

    world = _WORLDS.get(state.world_id)
    if world is None:
        raise KeyError(f"Unknown world id: {state.world_id}")

    # Resolve the roll using the default D&D 5e ruleset.  A more flexible
    # rules loading mechanism will be introduced in later phases.
    from engine.rules.dnd5e import DnD5eRules

    rules = DnD5eRules()
    dc = int(pending.get("dc") or 0)
    _success, _total = rules.resolve_player_roll(value, mod, dc)
    explanation = rules.format_roll_explanation(value, mod, dc)

    remember(state.memory, explanation)

    # Clear the pending roll before generating the next narration so that the
    # prompt does not include the guard line.
    state.pending_roll = None

    prompt_context = build_prompt(world, state)
    prompt = f"{SYSTEM_INSTRUCTIONS}\n{prompt_context}\n" f"System: {explanation}\nDM:"

    narration = await generate(model=model, prompt=prompt)

    try:  # pragma: no cover - optional dependency shim
        from engine.mechanics import detect_roll_request
    except Exception:  # pragma: no cover - executed only when module absent

        def detect_roll_request(_: str) -> Dict[str, Any] | None:
            return None

    roll_request_obj = detect_roll_request(narration)
    if roll_request_obj:
        roll_request = roll_request_obj.model_dump()
        roll_request["id"] = str(uuid.uuid4())
        awaiting_player_roll = True
    else:
        roll_request = None
        awaiting_player_roll = False

    state.pending_roll = roll_request
    remember(state.memory, narration)
    _GAME_STATES[game_id] = state

    return DMResponse(
        message=narration,
        awaiting_player_roll=awaiting_player_roll,
        roll_request=roll_request,
    )
