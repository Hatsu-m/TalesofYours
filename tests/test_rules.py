"""Tests for rule system implementations."""

from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

from engine.rules import CustomD6Rules, DnD5eRules, SimpleD20Rules


def test_dnd5e_roll_check_success():
    rules = DnD5eRules()
    success, total = rules.roll_check(bonus=3, dc=15, roll=12)
    assert success is True
    assert total == 15


def test_dnd5e_roll_check_natural_edges():
    rules = DnD5eRules()
    success, _ = rules.roll_check(bonus=100, dc=1, roll=1)
    assert success is False
    success, _ = rules.roll_check(bonus=-5, dc=100, roll=20)
    assert success is True


def test_dnd5e_apply_damage_floor():
    rules = DnD5eRules()
    assert rules.apply_damage(hp=5, damage=10) == 0


def test_custom_d6_roll_edges():
    rules = CustomD6Rules()
    success, _ = rules.roll_check(bonus=0, dc=4, roll=1)
    assert success is False
    success, _ = rules.roll_check(bonus=0, dc=10, roll=6)
    assert success is True


def test_format_explanation():
    rules = DnD5eRules()
    text = rules.format_roll_explanation(roll=10, bonus=2, dc=15)
    assert "rolled 10 + 2 = 12 vs DC 15" in text


def test_simple_d20_roll_check_and_cap():
    rules = SimpleD20Rules()
    success, total = rules.roll_check(bonus=8, dc=18, roll=12)
    assert success is True
    assert total == 18
    success, _ = rules.roll_check(bonus=0, dc=10, roll=5)
    assert success is False
    assert rules.apply_damage(hp=5, damage=10) == 0


def test_simple_d20_attack_damage_and_ammo():
    rules = SimpleD20Rules()
    hp, ammo, success, dmg = rules.resolve_attack(
        hp=10,
        bonus=0,
        dc=10,
        damage_die="1d6",
        ammo=2,
        roll=10,
        damage_roll=4,
    )
    assert success is True
    assert dmg == 4
    assert hp == 6
    assert ammo == 1


def test_simple_d20_attack_miss_no_damage():
    rules = SimpleD20Rules()
    hp, ammo, success, dmg = rules.resolve_attack(
        hp=10,
        bonus=0,
        dc=15,
        damage_die="1d6",
        ammo=2,
        roll=5,
        damage_roll=6,
    )
    assert success is False
    assert dmg == 0
    assert hp == 10
    assert ammo == 1


def test_simple_d20_attack_requires_ammo():
    rules = SimpleD20Rules()
    hp, ammo, success, dmg = rules.resolve_attack(
        hp=10,
        bonus=0,
        dc=10,
        damage_die="1d6",
        ammo=0,
        roll=15,
        damage_roll=6,
    )
    assert success is False
    assert dmg == 0
    assert hp == 10
    assert ammo == 0
