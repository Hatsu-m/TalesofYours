"""Test filtering of reasoning tokens in ollama client."""

from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

from server.app.llm.ollama_client import _strip_thinking_tags


def test_strip_thinking_tags():
    text = "Visible<think>hidden reasoning</think>output"
    assert _strip_thinking_tags(text) == "Visibleoutput"

