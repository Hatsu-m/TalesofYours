from __future__ import annotations

import json
from collections.abc import AsyncGenerator

import httpx

OLLAMA_API_URL = "http://localhost:11434"


async def list_models(client: httpx.AsyncClient | None = None) -> list[str]:
    """Return available Ollama model tags."""
    close_client = False
    if client is None:
        client = httpx.AsyncClient(base_url=OLLAMA_API_URL, timeout=None)
        close_client = True
    try:
        response = await client.get("/api/tags")
        response.raise_for_status()
        data = response.json()
        return [m["name"] for m in data.get("models", [])]
    finally:
        if close_client:
            await client.aclose()


async def generate(
    model: str,
    prompt: str,
    *,
    client: httpx.AsyncClient | None = None,
) -> str:
    """Generate text using the specified model."""
    close_client = False
    if client is None:
        client = httpx.AsyncClient(base_url=OLLAMA_API_URL, timeout=None)
        close_client = True
    try:
        response = await client.post(
            "/api/generate",
            json={"model": model, "prompt": prompt, "stream": False},
        )
        response.raise_for_status()
        data = response.json()
        return data.get("response", "")
    finally:
        if close_client:
            await client.aclose()


async def stream(
    model: str,
    prompt: str,
    *,
    client: httpx.AsyncClient | None = None,
) -> AsyncGenerator[str, None]:
    """Stream generated tokens from the model."""
    close_client = False
    if client is None:
        client = httpx.AsyncClient(base_url=OLLAMA_API_URL, timeout=None)
        close_client = True
    try:
        async with client.stream(
            "POST",
            "/api/generate",
            json={"model": model, "prompt": prompt, "stream": True},
        ) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if not line:
                    continue
                data = json.loads(line)
                token = data.get("response")
                if token:
                    yield token
    finally:
        if close_client:
            await client.aclose()
