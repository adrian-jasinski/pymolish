"""Group operation extensions: toggle, navigate, sort, copy, merge, extract."""

from __future__ import annotations

from pymolish.core.types import Category

CATEGORY = Category.GROUPS


def __init_plugin__(app: object | None = None) -> None:
    """Register group-manipulation commands. Empty in the Phase 1 scaffold."""
