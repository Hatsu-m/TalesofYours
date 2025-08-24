"""Turn orchestration service for the game engine."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Any, Dict

from engine.context import build_prompt
from engine.memory import MemoryItem, remember
from engine.world_loader import World, load_world_from_string
from engine.rules import get_ruleset

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

    def add_companion(self, companion: dict[str, Any]) -> None:
        """Add a companion to the party enforcing a maximum of three."""

        companions = [m for m in self.party if m.get("type") == "companion"]
        if len(companions) >= 3:
            raise ValueError("party already has maximum companions")
        data = {"type": "companion", **companion}
        self.party.append(data)

    def add_pet(self, pet: dict[str, Any]) -> None:
        """Add a pet to the party enforcing a maximum of two."""

        pets = [m for m in self.party if m.get("type") == "pet"]
        if len(pets) >= 2:
            raise ValueError("party already has maximum pets")
        data = {"type": "pet", **pet}
        self.party.append(data)


def list_worlds() -> list[dict[str, Any]]:
    """Return a minimal listing of available worlds."""

    return [
        {"id": wid, "title": w.title, "ruleset": w.ruleset}
        for wid, w in _WORLDS.items()
    ]


def import_world(markdown: str) -> int:
    """Import a world from Markdown text and return its identifier."""

    world = load_world_from_string(markdown)
    new_id = max(_WORLDS.keys(), default=0) + 1
    _WORLDS[new_id] = world
    return new_id


def validate_world(markdown: str) -> World:
    """Parse a world definition without persisting it."""

    return load_world_from_string(markdown)


def get_world(world_id: int) -> World:
    """Retrieve a world by identifier."""

    world = _WORLDS.get(world_id)
    if world is None:
        raise KeyError(f"Unknown world id: {world_id}")
    return world


def create_game(world_id: int) -> int:
    """Create a new game state for the given world."""

    if world_id not in _WORLDS:
        raise KeyError(f"Unknown world id: {world_id}")
    new_id = max(_GAME_STATES.keys(), default=0) + 1
    _GAME_STATES[new_id] = GameState(world_id=world_id, current_location=0)
    return new_id


def get_game_state(game_id: int) -> Dict[str, Any]:
    """Return the serialisable state for a game."""

    return export_game_state(game_id)


def add_companion(game_id: int, companion: Dict[str, Any]) -> None:
    """Add a companion to the specified game state."""

    state = _GAME_STATES.get(game_id)
    if state is None:
        raise KeyError(f"Unknown game id: {game_id}")
    state.add_companion(companion)


def remove_companion(game_id: int, companion_id: Any) -> None:
    """Remove a companion from the specified game state."""

    state = _GAME_STATES.get(game_id)
    if state is None:
        raise KeyError(f"Unknown game id: {game_id}")
    before = len(state.party)
    state.party = [
        m
        for m in state.party
        if not (m.get("type") == "companion" and m.get("id") == companion_id)
    ]
    if len(state.party) == before:
        raise KeyError(f"Unknown companion id: {companion_id}")


def export_game_state(game_id: int) -> Dict[str, Any]:
    """Return a serialisable representation of a game state."""

    state = _GAME_STATES.get(game_id)
    if state is None:
        raise KeyError(f"Unknown game id: {game_id}")
    return {
        "id": game_id,
        "world_id": state.world_id,
        "current_location": state.current_location,
        "party": state.party,
        "flags": state.flags,
        "timeline": state.timeline,
        "memory": [m.model_dump() for m in state.memory],
        "pending_roll": state.pending_roll,
    }


def import_game_state(data: Dict[str, Any]) -> int:
    """Create a new game from a previously exported state."""

    memory = [MemoryItem(**m) for m in data.get("memory", [])]
    state = GameState(
        world_id=int(data["world_id"]),
        current_location=int(data.get("current_location", 0)),
        party=list(data.get("party", [])),
        flags=dict(data.get("flags", {})),
        timeline=list(data.get("timeline", [])),
        memory=memory,
        pending_roll=data.get("pending_roll"),
    )
    new_id = max(_GAME_STATES.keys(), default=0) + 1
    _GAME_STATES[new_id] = state
    return new_id


@dataclass
class DMResponse:
    """Response returned after processing a turn."""

    message: str
    awaiting_player_roll: bool = False
    roll_request: Dict[str, Any] | None = None


SYSTEM_INSTRUCTIONS = (
    "You are a fair and impartial DM. "
    "Describe the world and the results of actions, "
    "but never roll for the player. "
    "Resolve companion and pet actions internally without requesting player rolls."
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
    rules = get_ruleset(world.ruleset)
    prompt_context = build_prompt(world, state)
    prompt = (
        f"{SYSTEM_INSTRUCTIONS}\n{rules.system_instructions}\n{prompt_context}\n"
        f"Player: {player_message}\nDM:"
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

    # Resolve the roll using the world's configured ruleset.
    rules = get_ruleset(world.ruleset)
    dc = int(pending.get("dc") or 0)
    _success, _total = rules.resolve_player_roll(value, mod, dc)
    explanation = rules.format_roll_explanation(value, mod, dc)

    remember(state.memory, explanation)

    # Clear the pending roll before generating the next narration so that the
    # prompt does not include the guard line.
    state.pending_roll = None

    prompt_context = build_prompt(world, state)
    prompt = (
        f"{SYSTEM_INSTRUCTIONS}\n{rules.system_instructions}\n{prompt_context}\n"
        f"System: {explanation}\nDM:"
    )

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
