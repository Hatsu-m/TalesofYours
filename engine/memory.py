"""Simple long-term memory system for game state."""

from __future__ import annotations

from typing import List

from pydantic import BaseModel


class MemoryItem(BaseModel):
    """Represents a single memory with an importance score."""

    content: str
    importance: float = 1.0


def remember(memories: List[MemoryItem], content: str, importance: float = 1.0) -> None:
    """Add a memory to the list."""
    memories.append(MemoryItem(content=content, importance=importance))


def recall(memories: List[MemoryItem], k: int = 5) -> List[MemoryItem]:
    """Return the top-K memories sorted by importance."""
    return sorted(memories, key=lambda m: m.importance, reverse=True)[:k]


def decay(memories: List[MemoryItem], rate: float = 0.9) -> None:
    """Decay the importance of all memories by ``rate``."""
    for memory in memories:
        memory.importance *= rate
