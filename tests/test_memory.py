"""Tests for memory management utilities."""

from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

from engine import memory


def test_recall_top_k():
    memories: list[memory.MemoryItem] = []
    memory.remember(memories, "a", importance=0.1)
    memory.remember(memories, "b", importance=0.5)
    memory.remember(memories, "c", importance=0.9)

    top = memory.recall(memories, k=2)
    assert [m.content for m in top] == ["c", "b"]


def test_decay_reduces_importance():
    memories: list[memory.MemoryItem] = []
    memory.remember(memories, "event", importance=1.0)
    memory.decay(memories, rate=0.5)
    top = memory.recall(memories, k=1)
    assert top[0].importance == 0.5
