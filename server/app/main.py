from fastapi import FastAPI, HTTPException
import httpx
from pydantic import BaseModel

from .engine_service import DMResponse, submit_player_roll
from .llm.ollama_client import list_models

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
