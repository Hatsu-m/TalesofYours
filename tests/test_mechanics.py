"""Tests for roll request detection."""

from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

from engine import mechanics


def test_detects_roll_request():
    text = "Roll a d20 for Perception (DC 15)"
    req = mechanics.detect_roll_request(text)
    assert req is not None
    assert req.sides == 20
    assert req.skill == "Perception"
    assert req.dc == 15


def test_no_roll_request():
    text = "The dragon snarls and watches you carefully."
    assert mechanics.detect_roll_request(text) is None


def test_detects_damage_roll_request():
    text = "Roll 1d8 damage"
    req = mechanics.detect_roll_request(text)
    assert req is not None
    assert req.sides == 8
    assert req.skill == "Damage"
    assert req.dc is None
