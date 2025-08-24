from pathlib import Path

from engine.world_loader import load_world


def test_load_world() -> None:
    world_path = Path(__file__).resolve().parents[1] / "worlds" / "sample_world.md"
    world = load_world(world_path)
    assert world.id == "sample"
    assert world.title == "Sample World"
    assert world.lore.startswith("A world of test")
    assert len(world.locations) == 2
    assert world.locations[0].name == "Town Square"
    assert any(npc.name == "Dragon" for npc in world.npcs)
