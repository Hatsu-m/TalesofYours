"""Base rules interface for game mechanics."""

from __future__ import annotations

from abc import ABC, abstractmethod


class RuleSystem(ABC):
    """Abstract base class for rule implementations."""

    @abstractmethod
    def roll_check(
        self, bonus: int, dc: int, roll: int | None = None
    ) -> tuple[bool, int]:
        """Perform a check for NPCs or monsters.

        Parameters
        ----------
        bonus:
            The modifier to apply to the roll.
        dc:
            Difficulty class to beat.
        roll:
            Optional predetermined die result for deterministic behaviour.

        Returns
        -------
        tuple[bool, int]
            A tuple of (success, total).
        """

    @abstractmethod
    def resolve_player_roll(self, roll: int, bonus: int, dc: int) -> tuple[bool, int]:
        """Resolve a roll supplied by the player."""

    @abstractmethod
    def apply_damage(self, hp: int, damage: int) -> int:
        """Apply damage to hit points and return the new value."""

    @property
    @abstractmethod
    def system_instructions(self) -> str:
        """Instructions describing the rule system for the LLM."""

    @abstractmethod
    def format_roll_explanation(self, roll: int, bonus: int, dc: int) -> str:
        """Human readable explanation of a roll."""
