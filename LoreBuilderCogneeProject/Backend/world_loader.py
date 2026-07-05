"""
world_loader.py – World Lore File Reader
=========================================
Discovers and reads world .md files from the WorldLoreFiles directory.
Returns clean world name → content mappings.
"""

from pathlib import Path
from typing import Dict

from Backend.config import WORLD_LORE_DIR


def get_world_names() -> list[str]:
    """
    Returns a sorted list of world names derived from the .md file stems.
    Example: "Aetheria (The Shattered Skies)" from the filename.
    """
    if not WORLD_LORE_DIR.exists():
        return []

    return sorted(
        p.stem  # filename without extension
        for p in WORLD_LORE_DIR.glob("*.md")
    )


def get_world_content(world_name: str) -> str:
    """
    Reads and returns the raw markdown content of a world file.
    Raises FileNotFoundError if the world does not exist.
    """
    world_file = WORLD_LORE_DIR / f"{world_name}.md"
    if not world_file.exists():
        raise FileNotFoundError(
            f"World file not found: {world_file}"
        )
    return world_file.read_text(encoding="utf-8")


def get_all_worlds() -> Dict[str, str]:
    """
    Returns a dict of { world_name: content } for all available worlds.
    """
    return {name: get_world_content(name) for name in get_world_names()}
