"""Shared type definitions and enums for the pymolish framework."""

from __future__ import annotations

from enum import Enum
from typing import Literal, TypeAlias

LogLevel: TypeAlias = Literal["info", "warn", "error"]
"""Permitted log levels accepted by :func:`pymolish.core.logging.plog`."""


class Category(str, Enum):
    """Canonical category labels used across the extension sub-packages."""

    IO = "I/O"
    GROUPS = "Groups"
    STRUCTURE = "Structure"
    SELECTION = "Selection"
    VISUALIZATION = "Visualization"
    ANIMATION = "Animation"
    META = "Meta"

    def __str__(self) -> str:  # noqa: D105
        return self.value


CategoryLike: TypeAlias = Category | str
"""Accept either the ``Category`` enum or a raw string for ergonomics."""
