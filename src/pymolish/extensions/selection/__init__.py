"""Selection helper extensions: sequence search and related commands."""

from __future__ import annotations

from ...core.autocompletion import AutocompletionRegistry
from ...core.registry import CommandRegistry
from ...core.types import Category

CATEGORY = Category.SELECTION


def __init_plugin__(app: object | None = None) -> None:
    """Register selection commands and their autocompletions."""
    from .sequence_search import search_sequence

    registry = CommandRegistry.instance()
    autocomplete = AutocompletionRegistry.instance()
    completers = autocomplete.completers

    registry.register(
        "search_sequence",
        search_sequence,
        category=CATEGORY,
        description=(
            "Search for amino acid sequences in loaded structures using alignment"
        ),
        examples=[
            "search_sequence MVLSPADKTNVKAA",
            "search_sequence ACDEFGH, mysel, 0.7",
            "search_sequence PEPTIDE, hit, 0.9",
        ],
        tags=["sequence", "alignment", "search", "biopython"],
        see_also=["pymolish_list", "pymolish_search"],
    )

    autocomplete.register("search_sequence", 0, completers.object_name, "sequence")
