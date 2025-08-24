"""Load structured world data from Markdown files."""

from __future__ import annotations

from pathlib import Path
from typing import List

import frontmatter
from markdown_it import MarkdownIt
from pydantic import BaseModel


class SectionEntry(BaseModel):
    """Generic entry with name and description."""

    name: str
    description: str


class World(BaseModel):
    """Structured world representation loaded from Markdown."""

    id: str
    title: str
    ruleset: str
    end_goal: str
    lore: str
    locations: List[SectionEntry]
    npcs: List[SectionEntry]
    factions: List[SectionEntry] = []
    items: List[SectionEntry] = []
    rules_notes: str | None = None


_md = MarkdownIt()


def _slice_section(
    tokens: list, start_idx: int, level: str, total_lines: int
) -> tuple[str, int, int]:
    title = tokens[start_idx + 1].content.strip()
    start_line = tokens[start_idx].map[1]
    end_line = total_lines
    for j in range(start_idx + 1, len(tokens)):
        t = tokens[j]
        if t.type == "heading_open" and t.tag == level:
            end_line = t.map[0]
            break
    return title, start_line, end_line


def _parse_sections(body: str) -> dict[str, str]:
    tokens = _md.parse(body)
    lines = body.splitlines()
    sections: dict[str, str] = {}
    for i, token in enumerate(tokens):
        if token.type == "heading_open" and token.tag == "h2":
            title, start, end = _slice_section(tokens, i, "h2", len(lines))
            sections[title] = "\n".join(lines[start:end]).strip()
    return sections


def _parse_entries(text: str) -> List[SectionEntry]:
    if not text:
        return []
    tokens = _md.parse(text)
    lines = text.splitlines()
    entries: List[SectionEntry] = []
    for i, token in enumerate(tokens):
        if token.type == "heading_open" and token.tag == "h3":
            name, start, end = _slice_section(tokens, i, "h3", len(lines))
            description = "\n".join(lines[start:end]).strip()
            entries.append(SectionEntry(name=name, description=description))
    return entries


def _build_world(post: frontmatter.Post) -> World:
    """Construct a :class:`World` instance from frontmatter ``Post`` data."""

    required = {"id", "title", "ruleset", "end_goal"}
    if not required.issubset(post.keys()):
        missing = required.difference(post.keys())
        raise ValueError(f"Missing frontmatter fields: {', '.join(sorted(missing))}")

    sections = _parse_sections(post.content)
    return World(
        id=str(post["id"]),
        title=str(post["title"]),
        ruleset=str(post["ruleset"]),
        end_goal=str(post["end_goal"]),
        lore=sections.get("Lore", ""),
        locations=_parse_entries(sections.get("Locations", "")),
        npcs=_parse_entries(sections.get("NPCs", "")),
        factions=_parse_entries(sections.get("Factions", "")),
        items=_parse_entries(sections.get("Items", "")),
        rules_notes=sections.get("Rules Notes"),
    )


def load_world(md_path: str | Path) -> World:
    """Load a world definition from a Markdown file."""

    post = frontmatter.load(md_path)
    return _build_world(post)


def load_world_from_string(text: str) -> World:
    """Load a world definition from a Markdown string."""

    post = frontmatter.loads(text)
    return _build_world(post)


def dump_world(world: World) -> str:
    """Serialise a :class:`World` back into Markdown format."""

    lines: list[str] = [
        "---",
        f"id: {world.id}",
        f"title: {world.title}",
        f"ruleset: {world.ruleset}",
        f"end_goal: {world.end_goal}",
        "---",
        "",
        "## Lore",
        world.lore,
    ]

    if world.locations:
        lines.append("\n## Locations")
        for entry in world.locations:
            lines.extend([f"\n### {entry.name}", entry.description])

    if world.npcs:
        lines.append("\n## NPCs")
        for entry in world.npcs:
            lines.extend([f"\n### {entry.name}", entry.description])

    if world.factions:
        lines.append("\n## Factions")
        for entry in world.factions:
            lines.extend([f"\n### {entry.name}", entry.description])

    if world.items:
        lines.append("\n## Items")
        for entry in world.items:
            lines.extend([f"\n### {entry.name}", entry.description])

    if world.rules_notes:
        lines.extend(["\n## Rules Notes", world.rules_notes])

    return "\n".join(lines) + "\n"


if __name__ == "__main__":  # pragma: no cover
    import argparse

    parser = argparse.ArgumentParser(description="Load and summarize a world file")
    parser.add_argument("path", help="Path to Markdown world file")
    args = parser.parse_args()
    world = load_world(args.path)
    print(world.model_dump_json(indent=2))
