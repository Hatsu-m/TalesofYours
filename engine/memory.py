"""Simple long-term memory system for game state."""

from __future__ import annotations

from typing import Iterable, List, Optional

from pydantic import BaseModel, Field


class MemoryItem(BaseModel):
    """Represents a single memory with an importance score and tags."""

    content: str
    importance: float = 1.0
    tags: List[str] = Field(default_factory=list)


def remember(
    memories: List[MemoryItem],
    content: str,
    importance: float = 1.0,
    tags: Optional[Iterable[str]] = None,
) -> None:
    """Add a memory to the list with optional ``tags``."""

    memories.append(
        MemoryItem(content=content, importance=importance, tags=list(tags or []))
    )


def recall(
    memories: List[MemoryItem],
    k: int = 5,
    tags: Optional[Iterable[str]] = None,
) -> List[MemoryItem]:
    """Return the top-K memories filtered by ``tags`` and sorted by importance."""

    items = memories
    if tags:
        tag_set = set(tags)
        items = [m for m in memories if tag_set.intersection(m.tags)]
    return sorted(items, key=lambda m: m.importance, reverse=True)[:k]


def decay(memories: List[MemoryItem], rate: float = 0.9) -> None:
    """Decay the importance of all memories by ``rate``."""
    for memory in memories:
        memory.importance *= rate
