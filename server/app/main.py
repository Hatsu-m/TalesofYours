from typing import Any, Dict

from fastapi import FastAPI, HTTPException, Response
import httpx
from pydantic import BaseModel

from .engine_service import (
    DMResponse,
    _WORLDS,
    export_game_state,
    import_game_state,
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


class PlayerRoll(BaseModel):
    request_id: str
    value: int
    mod: int = 0


@app.post("/games/{game_id}/player-roll")
async def player_roll(game_id: int, roll: PlayerRoll) -> DMResponse:
    try:
        return await submit_player_roll(game_id, roll.request_id, roll.value, roll.mod)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


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
    world = _WORLDS.get(world_id)
    if world is None:
        raise HTTPException(status_code=404, detail="Unknown world")
    return Response(content=dump_world(world), media_type="text/markdown")
