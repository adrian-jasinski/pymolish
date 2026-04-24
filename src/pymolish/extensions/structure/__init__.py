"""Structure analysis extensions: multialign, clean, cluster_ligands, fetch_uniprot."""

from __future__ import annotations

from pymolish.core.types import Category

CATEGORY = Category.STRUCTURE


def __init_plugin__(app: object | None = None) -> None:
    """Register structure-analysis commands. Empty in the Phase 1 scaffold."""
