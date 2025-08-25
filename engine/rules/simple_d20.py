"""Light-weight d20 rules with simple attack resolution."""

from __future__ import annotations

import random

from .base import RuleSystem


class SimpleD20Rules(RuleSystem):
    """Basic d20 mechanics with ammunition and damage dice."""

    MAX_BONUS = 6

    def roll_check(
        self, bonus: int, dc: int, roll: int | None = None
    ) -> tuple[bool, int]:
        roll = roll if roll is not None else random.randint(1, 20)
        capped = min(bonus, self.MAX_BONUS)
        total = roll + capped
        return total >= dc, total

    def resolve_player_roll(self, roll: int, bonus: int, dc: int) -> tuple[bool, int]:
        capped = min(bonus, self.MAX_BONUS)
        total = roll + capped
        return total >= dc, total

    def apply_damage(self, hp: int, damage: int) -> int:
        return max(hp - damage, 0)

    def _roll_damage(self, die: str, roll: int | None = None) -> int:
        count_str, size_str = die.lower().split("d")
        count = int(count_str) if count_str else 1
        size = int(size_str)
        if roll is not None:
            return roll
        return sum(random.randint(1, size) for _ in range(count))

    def resolve_attack(
        self,
        hp: int,
        bonus: int,
        dc: int,
        damage_die: str,
        ammo: int,
        roll: int | None = None,
        damage_roll: int | None = None,
    ) -> tuple[int, int, bool, int]:
        if ammo <= 0:
            return hp, ammo, False, 0
        success, _total = self.roll_check(bonus, dc, roll)
        ammo -= 1
        if success:
            damage = self._roll_damage(damage_die, damage_roll)
            hp = self.apply_damage(hp, damage)
            return hp, ammo, True, damage
        return hp, ammo, False, 0

    @property
    def system_instructions(self) -> str:  # pragma: no cover - static text
        return (
            "Roll a d20 and add modifiers up to +6. Checks succeed if the total "
            "meets or exceeds the DC. Attacks consume one ammo and roll weapon "
            "damage only on a hit."
        )

    def format_roll_explanation(self, roll: int, bonus: int, dc: int) -> str:
        capped = min(bonus, self.MAX_BONUS)
        total = roll + capped
        outcome = "success" if total >= dc else "failure"
        return f"rolled {roll} + {capped} = {total} vs DC {dc} -> {outcome}"
