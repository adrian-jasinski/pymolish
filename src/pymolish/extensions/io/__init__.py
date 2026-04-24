"""I/O extensions: batch file loading, export, format conversion.

Phase 2 will populate this package with ``load_files``, ``export_group``, and
``export_byres`` modules.
"""

from __future__ import annotations

from pymolish.core.types import Category

CATEGORY = Category.IO


def __init_plugin__(app: object | None = None) -> None:
    """Register I/O commands. Empty in the Phase 1 scaffold."""
