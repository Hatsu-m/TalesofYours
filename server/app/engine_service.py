"""Turn orchestration service for the game engine."""

from __future__ import annotations

import json
import re
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict

from engine.context import build_prompt
from engine.memory import MemoryItem, remember
from engine.world_loader import (
    World,
    SectionEntry,
    load_world,
    load_world_from_string,
)
from engine.rules import get_ruleset

from .llm.ollama_client import generate


_OPTION_RE = re.compile(r"^\s*(\d+)[.)]\s*(.+)")


def _extract_numbered_options(text: str) -> list[str]:
    """Parse numbered options from DM narration."""

    options: list[str] = []
    for line in text.splitlines():
        match = _OPTION_RE.match(line)
        if match:
            options.append(match.group(2).strip())
    return options


SAVE_DIR = Path(__file__).resolve().parents[2] / "saves"
SAVE_DIR.mkdir(parents=True, exist_ok=True)

WORLD_DIR = Path(__file__).resolve().parents[2] / "worlds"
WORLD_DIR.mkdir(parents=True, exist_ok=True)

_WORLD_FILES: dict[Path, int] = {}


# In-memory storage used as a temporary stand‑in for a database.  The
# surrounding application will eventually replace this with proper
# persistence but for now it allows ``run_turn`` to function in tests and
# examples without additional infrastructure.
_GAME_STATES: dict[int, "GameState"] = {}
_WORLDS: dict[int, World] = {}

MAX_HUNGER = 10
MAX_THIRST = 10
HUNGER_DECAY_SECONDS = 3600
THIRST_DECAY_SECONDS = 1800
NEEDS_DAMAGE = 1
TURN_TIME_SECONDS = 60


def _validate_stats(world: World, stats: Dict[str, Any]) -> None:
    """Ensure stats conform to world configuration and ruleset limits."""

    allowed = set(world.stats)
    max_bonus = getattr(get_ruleset(world.ruleset), "MAX_BONUS", None)
    for key, value in stats.items():
        if key in {"hp", "hunger", "thirst"}:
            continue
        if allowed and key not in allowed:
            raise ValueError(f"unknown stat: {key}")
        if max_bonus is not None and value > max_bonus:
            raise ValueError(f"stat {key} exceeds maximum {max_bonus}")


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
    elapsed_time: float = 0.0
    last_needs_update: float = 0.0
    last_options: list[str] = field(default_factory=list)

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


def _update_survival_needs(state: GameState, now: float | None = None) -> None:
    """Update hunger and thirst based on elapsed in-game time."""

    if now is None:
        now = state.elapsed_time
    elapsed = now - state.last_needs_update
    hunger_ticks = int(elapsed // HUNGER_DECAY_SECONDS)
    thirst_ticks = int(elapsed // THIRST_DECAY_SECONDS)
    if hunger_ticks == 0 and thirst_ticks == 0:
        return

    for member in state.party:
        stats = member.setdefault("stats", {})
        hunger = stats.get("hunger", MAX_HUNGER)
        thirst = stats.get("thirst", MAX_THIRST)

        new_hunger = max(hunger - hunger_ticks, 0)
        hunger_damage = max(hunger_ticks - hunger, 0)

        new_thirst = max(thirst - thirst_ticks, 0)
        thirst_damage = max(thirst_ticks - thirst, 0)

        stats["hunger"] = new_hunger
        stats["thirst"] = new_thirst

        total_damage = (hunger_damage + thirst_damage) * NEEDS_DAMAGE
        if total_damage:
            stats["hp"] = stats.get("hp", 0) - total_damage

    state.last_needs_update = now


def _advance_time(state: GameState, seconds: float) -> None:
    """Advance in-game time and update survival needs."""

    state.elapsed_time += seconds
    _update_survival_needs(state)


def advance_time(game_id: int, seconds: float) -> None:
    """Public API to advance time for a game."""

    state = _GAME_STATES.get(game_id)
    if state is None:
        raise KeyError(f"Unknown game id: {game_id}")
    _advance_time(state, seconds)


def _load_world_files() -> None:
    """Load world definitions from markdown files into memory."""

    for path in WORLD_DIR.glob("*.md"):
        if path in _WORLD_FILES:
            continue
        try:
            world = load_world(path)
        except Exception:
            continue
        new_id = max(_WORLDS.keys(), default=0) + 1
        _WORLD_FILES[path] = new_id
        _WORLDS[new_id] = world


def list_worlds() -> list[dict[str, Any]]:
    """Return a minimal listing of available worlds."""

    _load_world_files()
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
    state = _GAME_STATES.get(game_id)
    if state is None:
        raise KeyError(f"Unknown game id: {game_id}")
    _update_survival_needs(state)
    return export_game_state(game_id)


def add_companion(game_id: int, companion: Dict[str, Any]) -> None:
    """Add a companion to the specified game state."""

    state = _GAME_STATES.get(game_id)
    if state is None:
        raise KeyError(f"Unknown game id: {game_id}")
    _update_survival_needs(state)
    world = _WORLDS[state.world_id]
    stats = companion.get("stats")
    if stats:
        _validate_stats(world, stats)
    state.add_companion(companion)


def remove_companion(game_id: int, companion_id: Any) -> None:
    """Remove a companion from the specified game state."""

    state = _GAME_STATES.get(game_id)
    if state is None:
        raise KeyError(f"Unknown game id: {game_id}")
    _update_survival_needs(state)
    before = len(state.party)
    state.party = [
        m
        for m in state.party
        if not (m.get("type") == "companion" and m.get("id") == companion_id)
    ]
    if len(state.party) == before:
        raise KeyError(f"Unknown companion id: {companion_id}")


def update_party_member(game_id: int, member_id: Any, updates: Dict[str, Any]) -> None:
    """Update fields for a specific party member.

    Parameters
    ----------
    game_id:
        Identifier of the game state to modify.
    member_id:
        Identifier of the party member within the game state's ``party`` list.
    updates:
        Mapping of fields to merge into the member record.
    """

    state = _GAME_STATES.get(game_id)
    if state is None:
        raise KeyError(f"Unknown game id: {game_id}")
    _update_survival_needs(state)
    for member in state.party:
        if member.get("id") == member_id:
            if "stats" in updates:
                world = _WORLDS[state.world_id]
                stats_update = updates.pop("stats") or {}
                _validate_stats(world, stats_update)
                stats = member.setdefault("stats", {})
                stats.update(stats_update)
                stats["hunger"] = min(stats.get("hunger", MAX_HUNGER), MAX_HUNGER)
                stats["thirst"] = min(stats.get("thirst", MAX_THIRST), MAX_THIRST)
            member.update(updates)
            return
    raise KeyError(f"Unknown party member id: {member_id}")


def feed_member(game_id: int, member_id: Any, amount: int = MAX_HUNGER) -> None:
    """Increase a party member's hunger level."""

    state = _GAME_STATES.get(game_id)
    if state is None:
        raise KeyError(f"Unknown game id: {game_id}")
    _update_survival_needs(state)
    for member in state.party:
        if member.get("id") == member_id:
            stats = member.setdefault("stats", {})
            stats["hunger"] = min(stats.get("hunger", MAX_HUNGER) + amount, MAX_HUNGER)
            return
    raise KeyError(f"Unknown party member id: {member_id}")


def hydrate_member(game_id: int, member_id: Any, amount: int = MAX_THIRST) -> None:
    """Increase a party member's thirst level."""

    state = _GAME_STATES.get(game_id)
    if state is None:
        raise KeyError(f"Unknown game id: {game_id}")
    _update_survival_needs(state)
    for member in state.party:
        if member.get("id") == member_id:
            stats = member.setdefault("stats", {})
            stats["thirst"] = min(stats.get("thirst", MAX_THIRST) + amount, MAX_THIRST)
            return
    raise KeyError(f"Unknown party member id: {member_id}")


def update_world(world_id: int, updates: Dict[str, Any]) -> None:
    """Apply partial updates to a world definition."""

    world = _WORLDS.get(world_id)
    if world is None:
        raise KeyError(f"Unknown world id: {world_id}")

    if "npcs" in updates:
        world.npcs = [SectionEntry(**n) for n in updates.pop("npcs")]
    for key, value in updates.items():
        setattr(world, key, value)


def update_game_state(game_id: int, updates: Dict[str, Any]) -> None:
    """Apply partial updates to a game state."""

    state = _GAME_STATES.get(game_id)
    if state is None:
        raise KeyError(f"Unknown game id: {game_id}")
    _update_survival_needs(state)

    if "current_location" in updates:
        state.current_location = int(updates["current_location"])
    if "party" in updates:
        world = _WORLDS[state.world_id]
        party = list(updates["party"])
        for member in party:
            stats = member.get("stats")
            if stats:
                _validate_stats(world, stats)
                stats["hunger"] = min(stats.get("hunger", MAX_HUNGER), MAX_HUNGER)
                stats["thirst"] = min(stats.get("thirst", MAX_THIRST), MAX_THIRST)
        state.party = party
    if "flags" in updates:
        state.flags.update(updates["flags"])
    if "memory" in updates:
        state.memory = [MemoryItem(**m) for m in updates["memory"]]


STATE_UPDATE_PREFIX = "STATE_UPDATE:"


def _apply_state_updates(state: GameState, updates: Dict[str, Any]) -> None:
    """Merge structured updates into the game state."""

    for member_update in updates.get("party", []):
        member_id = member_update.get("id")
        for member in state.party:
            if member.get("id") == member_id:
                if "stats" in member_update:
                    world = _WORLDS[state.world_id]
                    _validate_stats(world, member_update["stats"])
                    stats = member.setdefault("stats", {})
                    stats.update(member_update["stats"])
                    stats["hunger"] = min(stats.get("hunger", MAX_HUNGER), MAX_HUNGER)
                    stats["thirst"] = min(stats.get("thirst", MAX_THIRST), MAX_THIRST)
                if "inventory" in member_update:
                    inv_update = member_update["inventory"]
                    inventory = member.setdefault("inventory", [])
                    for item in inv_update.get("add", []):
                        if item not in inventory:
                            inventory.append(item)
                    for item in inv_update.get("remove", []):
                        if item in inventory:
                            inventory.remove(item)
                break

    if "flags" in updates:
        state.flags.update(updates["flags"])
    if "current_location" in updates:
        state.current_location = int(updates["current_location"])


def _extract_state_updates(state: GameState, narration: str) -> str:
    """Strip state update markers from narration and apply them."""

    lines = narration.splitlines()
    kept: list[str] = []
    for line in lines:
        if line.startswith(STATE_UPDATE_PREFIX):
            json_part = line[len(STATE_UPDATE_PREFIX) :].strip()
            try:
                updates = json.loads(json_part)
                _apply_state_updates(state, updates)
            except Exception:  # pragma: no cover - invalid update format
                pass
        else:
            kept.append(line)
    return "\n".join(kept).strip()


def _transcript_path(game_id: int) -> Path:
    return SAVE_DIR / f"game_{game_id}.jsonl"


def _autosave_path(game_id: int) -> Path:
    return SAVE_DIR / f"game_{game_id}.json"


def append_transcript(game_id: int, actor: str, text: str) -> None:
    entry = {"actor": actor, "text": text}
    path = _transcript_path(game_id)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry) + "\n")


def autosave_game_state(game_id: int) -> None:
    data = export_game_state(game_id)
    path = _autosave_path(game_id)
    with path.open("w", encoding="utf-8") as fh:
        json.dump(data, fh)


def load_autosave(game_id: int) -> None:
    path = _autosave_path(game_id)
    if not path.exists():
        raise FileNotFoundError(f"No autosave for game {game_id}")
    data = json.loads(path.read_text(encoding="utf-8"))
    _GAME_STATES[game_id] = _deserialize_game_state(data)


def list_saved_games() -> list[dict[str, int]]:
    """Return identifiers for saved games on disk."""
    games: list[dict[str, int]] = []
    for path in SAVE_DIR.glob("game_*.json"):
        try:
            game_id = int(path.stem.split("_")[1])
            data = json.loads(path.read_text(encoding="utf-8"))
            world_id = int(data["world_id"])
        except (IndexError, KeyError, ValueError, json.JSONDecodeError):
            continue
        games.append({"id": game_id, "world_id": world_id})
    return games


def _deserialize_game_state(data: Dict[str, Any]) -> GameState:
    memory = [MemoryItem(**m) for m in data.get("memory", [])]
    return GameState(
        world_id=int(data["world_id"]),
        current_location=int(data.get("current_location", 0)),
        party=list(data.get("party", [])),
        flags=dict(data.get("flags", {})),
        timeline=list(data.get("timeline", [])),
        memory=memory,
        pending_roll=data.get("pending_roll"),
        elapsed_time=float(data.get("elapsed_time", 0.0)),
        last_needs_update=float(data.get("last_needs_update", 0.0)),
        last_options=list(data.get("last_options", [])),
    )


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
        "elapsed_time": state.elapsed_time,
        "last_needs_update": state.last_needs_update,
        "last_options": state.last_options,
    }


def import_game_state(data: Dict[str, Any]) -> int:
    """Create a new game from a previously exported state."""

    state = _deserialize_game_state(data)
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
    "When a roll is required, ask the player to roll and wait for their response "
    "before narrating outcomes. "
    "If an attack hits, have the player roll for damage instead of rolling it "
    "yourself. "
    "Resolve companion and pet actions internally without requesting player rolls. "
    "Whenever the player must choose a next step, present three logical, numbered "
    "options and note that they may always suggest another action. "
    "Before awarding loot, instruct the player to roll to determine its quality."
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
    _advance_time(state, TURN_TIME_SECONDS)

    # Allow numeric responses to select previously offered options.
    stripped = player_message.strip()
    if stripped.isdigit() and state.last_options:
        idx = int(stripped) - 1
        if 0 <= idx < len(state.last_options):
            player_message = state.last_options[idx]

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
    narration = _extract_state_updates(state, narration)

    # Attempt to detect roll requests.  This module is introduced in a
    # later phase of development, so we fail gracefully if it is missing.
    try:  # pragma: no cover - simple optional dependency shim
        from engine import mechanics
    except Exception:  # pragma: no cover - executed only when module absent

        class _MechanicsFallback:
            @staticmethod
            def detect_roll_request(_: str) -> Dict[str, Any] | None:
                return None

            _ROLL_RE = None

        mechanics = _MechanicsFallback()

    roll_request_obj = mechanics.detect_roll_request(narration)
    if roll_request_obj:
        roll_re = getattr(mechanics, "_ROLL_RE", None)
        if roll_re:
            match = roll_re.search(narration)
            if match:
                end = match.end()
                while end < len(narration) and narration[end] in ".!? ":
                    end += 1
                narration = narration[:end].rstrip()
        roll_request = roll_request_obj.model_dump()
        roll_request["id"] = str(uuid.uuid4())
        awaiting_player_roll = True
    else:
        roll_request = None
        awaiting_player_roll = False
    state.pending_roll = roll_request

    # Track any numbered options for the next turn.
    state.last_options = _extract_numbered_options(narration)

    # Store narration in long‑term memory.
    remember(state.memory, narration)

    # Persist the updated state.
    _GAME_STATES[game_id] = state

    append_transcript(game_id, "player", player_message)
    append_transcript(game_id, "dm", narration)
    autosave_game_state(game_id)

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

    _update_survival_needs(state)

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
    narration = _extract_state_updates(state, narration)

    try:  # pragma: no cover - optional dependency shim
        from engine import mechanics
    except Exception:  # pragma: no cover - executed only when module absent

        class _MechanicsFallback:
            @staticmethod
            def detect_roll_request(_: str) -> Dict[str, Any] | None:
                return None

            _ROLL_RE = None

        mechanics = _MechanicsFallback()

    roll_request_obj = mechanics.detect_roll_request(narration)
    if roll_request_obj:
        roll_re = getattr(mechanics, "_ROLL_RE", None)
        if roll_re:
            match = roll_re.search(narration)
            if match:
                end = match.end()
                while end < len(narration) and narration[end] in ".!? ":
                    end += 1
                narration = narration[:end].rstrip()
        roll_request = roll_request_obj.model_dump()
        roll_request["id"] = str(uuid.uuid4())
        awaiting_player_roll = True
    else:
        roll_request = None
        awaiting_player_roll = False

    state.pending_roll = roll_request
    state.last_options = _extract_numbered_options(narration)
    remember(state.memory, narration)
    _GAME_STATES[game_id] = state

    append_transcript(game_id, "player", f"roll {value} (mod {mod})")
    append_transcript(game_id, "system", explanation)
    append_transcript(game_id, "dm", narration)
    autosave_game_state(game_id)

    return DMResponse(
        message=narration,
        awaiting_player_roll=awaiting_player_roll,
        roll_request=roll_request,
    )
