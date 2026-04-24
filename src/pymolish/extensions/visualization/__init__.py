"""Color and visualization extensions: palettes, color_group, color_ss."""

from __future__ import annotations

from pymolish.core.types import Category

CATEGORY = Category.VISUALIZATION


def __init_plugin__(app: object | None = None) -> None:
    """Register visualization commands. Empty in the Phase 1 scaffold."""
