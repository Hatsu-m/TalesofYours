"""Simple d6-based rule example."""

from __future__ import annotations

import random

from .base import RuleSystem


class CustomD6Rules(RuleSystem):
    """Light‑weight custom rule system using a single d6."""

    def roll_check(
        self, bonus: int, dc: int, roll: int | None = None
    ) -> tuple[bool, int]:
        roll = roll if roll is not None else random.randint(1, 6)
        total = roll + bonus
        if roll == 1:
            return False, total
        if roll == 6:
            return True, total
        return total >= dc, total

    def resolve_player_roll(self, roll: int, bonus: int, dc: int) -> tuple[bool, int]:
        total = roll + bonus
        if roll == 1:
            return False, total
        if roll == 6:
            return True, total
        return total >= dc, total

    def apply_damage(self, hp: int, damage: int) -> int:
        return max(hp - damage, 0)

    @property
    def system_instructions(self) -> str:  # pragma: no cover - static text
        return "Roll a single d6 for checks. A 6 always succeeds and a 1 always fails."

    def format_roll_explanation(self, roll: int, bonus: int, dc: int) -> str:
        total = roll + bonus
        outcome = "success" if (roll == 6 or (roll != 1 and total >= dc)) else "failure"
        return f"rolled {roll} + {bonus} = {total} vs DC {dc} -> {outcome}"
