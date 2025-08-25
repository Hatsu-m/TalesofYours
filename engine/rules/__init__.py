"""Rules engine implementations."""

from .base import RuleSystem
from .dnd5e import DnD5eRules
from .custom_d6 import CustomD6Rules
from .simple_d20 import SimpleD20Rules

_RULESET_MAP = {
    "dnd5e": DnD5eRules,
    "custom_d6": CustomD6Rules,
    "simple_d20": SimpleD20Rules,
}


def get_ruleset(name: str) -> RuleSystem:
    """Return an instance of the ruleset ``name``.

    Parameters
    ----------
    name:
        Identifier of the ruleset such as ``"dnd5e"`` or ``"custom_d6"``.

    Returns
    -------
    RuleSystem
        Instantiated rules engine implementation.
    """

    cls = _RULESET_MAP.get(name.lower())
    if cls is None:
        raise ValueError(f"Unknown ruleset: {name}")
    return cls()


__all__ = [
    "RuleSystem",
    "DnD5eRules",
    "CustomD6Rules",
    "SimpleD20Rules",
    "get_ruleset",
]
