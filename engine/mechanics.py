"""Game mechanics utilities."""

from __future__ import annotations

import re
from typing import Optional

from pydantic import BaseModel


class RollRequest(BaseModel):
    """Data describing a player roll request detected in DM text."""

    skill: str
    sides: int
    dc: Optional[int] = None


_ROLL_RE = re.compile(
    r"roll\s+(?:a|an)?\s*d(?P<die>\d+)\s+for\s+"
    r"(?P<skill>[^()]+)"
    r"(?:\s*\(dc\s*(?P<dc>\d+)\))?",
    re.IGNORECASE,
)


def detect_roll_request(dm_text: str) -> Optional[RollRequest]:
    """Detect a roll request in DM text.

    Parameters
    ----------
    dm_text:
        The narration from the DM.

    Returns
    -------
    Optional[RollRequest]
        Parsed roll request if one is detected, otherwise ``None``.
    """

    match = _ROLL_RE.search(dm_text)
    if not match:
        return None

    sides = int(match.group("die"))
    skill = match.group("skill").strip().title()
    dc_str = match.group("dc")
    dc = int(dc_str) if dc_str is not None else None

    return RollRequest(skill=skill, sides=sides, dc=dc)
