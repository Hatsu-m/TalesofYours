from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
import httpx
from pydantic import BaseModel
from typing import Any, Dict
import logging

from .engine_service import (
    DMResponse,
    add_companion,
    create_game,
    export_game_state,
    get_game_state,
    get_world,
    import_game_state,
    import_world,
    validate_world,
    list_worlds,
    remove_companion,
    run_turn,
    submit_player_roll,
    update_party_member,
    update_world,
    update_game_state,
)
from .llm.ollama_client import list_models
from engine.world_loader import dump_world

logger = logging.getLogger(__name__)
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/health/llm")
async def llm_health() -> dict[str, list[str]]:
    try:
        models = await list_models()
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=503, detail="Ollama unavailable") from exc
    return {"models": models}


@app.get("/worlds")
def worlds() -> list[dict[str, Any]]:
    """List all available worlds."""

    return list_worlds()


class WorldImport(BaseModel):
    content: str


@app.post("/worlds/import")
def import_world_endpoint(payload: WorldImport) -> dict[str, int]:
    try:
        new_id = import_world(payload.content)
    except Exception as exc:  # pragma: no cover - logging path
        logger.exception("world import failed")
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"id": new_id}


@app.post("/worlds/validate")
def validate_world_endpoint(payload: WorldImport) -> Dict[str, Any]:
    try:
        world = validate_world(payload.content)
    except Exception as exc:  # pragma: no cover - logging path
        logger.exception("world validation failed")
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return world.model_dump()


@app.get("/worlds/{world_id}")
def get_world_endpoint(world_id: int) -> Dict[str, Any]:
    try:
        world = get_world(world_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return world.model_dump()


class WorldUpdate(BaseModel):
    title: str | None = None
    ruleset: str | None = None
    lore: str | None = None
    npcs: list[Dict[str, str]] | None = None
    rules_notes: str | None = None
    stats: list[str] | None = None


@app.patch("/worlds/{world_id}")
def update_world_endpoint(world_id: int, payload: WorldUpdate) -> dict[str, str]:
    try:
        update_world(world_id, payload.model_dump(exclude_unset=True))
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {"status": "ok"}


class PlayerRoll(BaseModel):
    request_id: str
    value: int
    mod: int = 0


class GameCreate(BaseModel):
    world_id: int


@app.post("/games")
def create_game_endpoint(payload: GameCreate) -> dict[str, int]:
    try:
        new_id = create_game(payload.world_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {"id": new_id}


@app.get("/games/{game_id}")
def get_game_endpoint(game_id: int) -> Dict[str, Any]:
    try:
        return get_game_state(game_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


class TurnRequest(BaseModel):
    message: str
    model: str = "llama3"


@app.post("/games/{game_id}/turn")
async def game_turn(game_id: int, payload: TurnRequest) -> DMResponse:
    try:
        return await run_turn(game_id, payload.message, model=payload.model)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.post("/games/{game_id}/player-roll")
async def player_roll(game_id: int, roll: PlayerRoll) -> DMResponse:
    try:
        return await submit_player_roll(game_id, roll.request_id, roll.value, roll.mod)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


class CompanionPayload(BaseModel):
    id: int
    name: str
    persona: str


@app.post("/games/{game_id}/companions")
def add_companion_endpoint(game_id: int, companion: CompanionPayload) -> dict[str, str]:
    try:
        add_companion(game_id, companion.model_dump())
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"status": "ok"}


@app.delete("/games/{game_id}/companions/{companion_id}")
def remove_companion_endpoint(game_id: int, companion_id: int) -> dict[str, str]:
    try:
        remove_companion(game_id, companion_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {"status": "ok"}


class PartyMemberUpdate(BaseModel):
    name: str | None = None
    stats: Dict[str, Any] | None = None
    inventory: list[str] | None = None
    status: str | None = None


@app.patch("/games/{game_id}/party/{member_id}")
def update_party_member_endpoint(
    game_id: int, member_id: int, payload: PartyMemberUpdate
) -> dict[str, str]:
    try:
        update_party_member(game_id, member_id, payload.model_dump(exclude_unset=True))
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"status": "ok"}


class GameUpdate(BaseModel):
    current_location: int | None = None
    party: list[Dict[str, Any]] | None = None
    memory: list[Dict[str, Any]] | None = None
    flags: Dict[str, Any] | None = None


@app.patch("/games/{game_id}")
def update_game_endpoint(game_id: int, payload: GameUpdate) -> dict[str, str]:
    try:
        update_game_state(game_id, payload.model_dump(exclude_unset=True))
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"status": "ok"}


@app.get("/games/{game_id}/save")
def save_game(game_id: int) -> Dict[str, Any]:
    try:
        return export_game_state(game_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


class GameImport(BaseModel):
    state: Dict[str, Any]


@app.post("/games/import")
def import_game(payload: GameImport) -> Dict[str, int]:
    try:
        new_id = import_game_state(payload.state)
    except Exception as exc:  # pragma: no cover - logging path
        logger.exception("game import failed")
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"id": new_id}


@app.get("/worlds/{world_id}/export")
def export_world(world_id: int) -> Response:
    try:
        world = get_world(world_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return Response(content=dump_world(world), media_type="text/markdown")
