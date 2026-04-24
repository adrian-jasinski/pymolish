"""Selection helper extensions: sequence_search, etc."""

from __future__ import annotations

from pymolish.core.types import Category

CATEGORY = Category.SELECTION


def __init_plugin__(app: object | None = None) -> None:
    """Register selection commands. Empty in the Phase 1 scaffold."""
