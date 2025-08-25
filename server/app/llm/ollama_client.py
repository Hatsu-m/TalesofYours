from __future__ import annotations

import json
from collections.abc import AsyncGenerator
import re

import httpx

OLLAMA_API_URL = "http://localhost:11434"

_THINK_START = "<think>"
_THINK_END = "</think>"


def _strip_thinking_tags(text: str) -> str:
    """Remove `<think>` sections from ``text``."""
    pattern = re.compile(rf"{re.escape(_THINK_START)}.*?{re.escape(_THINK_END)}", re.DOTALL)
    return re.sub(pattern, "", text)


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
        raw = data.get("response", "")
        return _strip_thinking_tags(raw)
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
            buffer = ""
            in_think = False
            async for line in response.aiter_lines():
                if not line:
                    continue
                data = json.loads(line)
                token = data.get("response")
                if not token:
                    continue
                buffer += token
                while buffer:
                    if in_think:
                        end_idx = buffer.find(_THINK_END)
                        if end_idx == -1:
                            buffer = ""
                            break
                        buffer = buffer[end_idx + len(_THINK_END) :]
                        in_think = False
                    else:
                        start_idx = buffer.find(_THINK_START)
                        if start_idx == -1:
                            yield buffer
                            buffer = ""
                            break
                        if start_idx > 0:
                            yield buffer[:start_idx]
                        buffer = buffer[start_idx + len(_THINK_START) :]
                        in_think = True
            if buffer and not in_think:
                yield buffer
    finally:
        if close_client:
            await client.aclose()
