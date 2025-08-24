from fastapi import FastAPI, HTTPException, Response
import httpx
from pydantic import BaseModel
from typing import Any, Dict

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
)
from .llm.ollama_client import list_models
from engine.world_loader import dump_world

app = FastAPI()


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
    new_id = import_world(payload.content)
    return {"id": new_id}


@app.post("/worlds/validate")
def validate_world_endpoint(payload: WorldImport) -> Dict[str, Any]:
    try:
        world = validate_world(payload.content)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return world.model_dump()


@app.get("/worlds/{world_id}")
def get_world_endpoint(world_id: int) -> Dict[str, Any]:
    try:
        world = get_world(world_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return world.model_dump()


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
    new_id = import_game_state(payload.state)
    return {"id": new_id}


@app.get("/worlds/{world_id}/export")
def export_world(world_id: int) -> Response:
    try:
        world = get_world(world_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return Response(content=dump_world(world), media_type="text/markdown")
