from fastapi import FastAPI, HTTPException
import httpx

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
