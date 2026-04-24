"""Movie and animation extensions: transparency, movie_group."""

from __future__ import annotations

from pymolish.core.types import Category

CATEGORY = Category.ANIMATION


def __init_plugin__(app: object | None = None) -> None:
    """Register animation commands. Empty in the Phase 1 scaffold."""
