"""Animation extensions: transparency animation and movie-from-group."""

from __future__ import annotations

from ...core.autocompletion import AutocompletionRegistry
from ...core.registry import CommandRegistry
from ...core.types import Category

CATEGORY = Category.ANIMATION

# Local lambda completers for transparency-type and direction arguments.
_TRANSPARENCY_TYPES = lambda t: [  # noqa: E731
    s for s in ["0", "1", "2", "3"] if s.startswith(t)
]
_DIRECTIONS = lambda t: [  # noqa: E731
    s for s in ["increase", "decrease"] if s.startswith(t)
]


def __init_plugin__(app: object | None = None) -> None:
    """Register animation commands and their autocompletions."""
    from .movie_group import movie_from_group
    from .transparency import (
        fade_in,
        fade_out,
        movie_transparency,
        set_frame_transparency,
        suggest_transparency_type,
        transparency_pulse,
        transparency_range,
        transparency_sequence,
    )

    registry = CommandRegistry.instance()
    autocomplete = AutocompletionRegistry.instance()
    completers = autocomplete.completers

    # ------------------------------------------------------------------
    # movie_transparency
    # ------------------------------------------------------------------
    registry.register(
        "movie_transparency",
        movie_transparency,
        category=CATEGORY,
        description="Animate transparency linearly over a frame range",
        examples=[
            "movie_transparency protein, 10, 50, 0.0, 1.0, 1",
            "movie_transparency ligand, 1, 100, 0.5, 0.0, 2, decrease",
            "movie_transparency all, 1, 30",
        ],
        tags=["animation", "transparency", "movie", "fade"],
        see_also=[
            "fade_in",
            "fade_out",
            "transparency_pulse",
            "set_frame_transparency",
        ],
    )

    # ------------------------------------------------------------------
    # fade_in / fade_out
    # ------------------------------------------------------------------
    registry.register(
        "fade_in",
        fade_in,
        category=CATEGORY,
        description="Fade objects in (decrease transparency from 1.0 to 0.0)",
        examples=[
            "fade_in protein, 1, 30",
            "fade_in ligand, 10, 50, 1",
        ],
        tags=["animation", "fade", "transparency", "movie"],
        see_also=["fade_out", "movie_transparency"],
    )

    registry.register(
        "fade_out",
        fade_out,
        category=CATEGORY,
        description="Fade objects out (increase transparency from 0.0 to 1.0)",
        examples=[
            "fade_out protein, 1, 30",
            "fade_out complex, 20, 60, 1",
        ],
        tags=["animation", "fade", "transparency", "movie"],
        see_also=["fade_in", "movie_transparency"],
    )

    # ------------------------------------------------------------------
    # transparency_pulse
    # ------------------------------------------------------------------
    registry.register(
        "transparency_pulse",
        transparency_pulse,
        category=CATEGORY,
        description="Create a pulsing transparency effect over multiple cycles",
        examples=[
            "transparency_pulse protein, 1, 60",
            "transparency_pulse ligand, 1, 90, 0.2, 0.8, 1, 3",
        ],
        tags=["animation", "transparency", "pulse", "movie"],
        see_also=["fade_in", "fade_out", "movie_transparency"],
    )

    # ------------------------------------------------------------------
    # suggest_transparency_type
    # ------------------------------------------------------------------
    registry.register(
        "suggest_transparency_type",
        suggest_transparency_type,
        category=CATEGORY,
        description="Suggest the best transparency type for a selection",
        examples=[
            "suggest_transparency_type",
            "suggest_transparency_type protein",
            "suggest_transparency_type ligand_binding_site",
        ],
        tags=["animation", "transparency", "suggest", "utility"],
        see_also=["movie_transparency", "set_frame_transparency"],
    )

    # ------------------------------------------------------------------
    # set_frame_transparency
    # ------------------------------------------------------------------
    registry.register(
        "set_frame_transparency",
        set_frame_transparency,
        category=CATEGORY,
        description="Set transparency for a single specific frame",
        examples=[
            "set_frame_transparency protein, 50, 0.5, 1",
            "set_frame_transparency complex, 100, 0.8, 0",
        ],
        tags=["animation", "transparency", "frame", "movie"],
        see_also=["movie_transparency", "transparency_sequence", "transparency_range"],
    )

    # ------------------------------------------------------------------
    # transparency_sequence
    # ------------------------------------------------------------------
    registry.register(
        "transparency_sequence",
        transparency_sequence,
        category=CATEGORY,
        description="Set transparency for multiple frames via frame:value pairs",
        examples=[
            "transparency_sequence protein, 100:0.0,110:0.5,120:1.0, 1",
            "transparency_sequence chain A, 1:0.2,5:0.6,10:1.0, 0",
        ],
        tags=["animation", "transparency", "sequence", "movie"],
        see_also=["set_frame_transparency", "movie_transparency", "transparency_range"],
    )

    # ------------------------------------------------------------------
    # transparency_range
    # ------------------------------------------------------------------
    registry.register(
        "transparency_range",
        transparency_range,
        category=CATEGORY,
        description="Set transparency across a frame range with a fixed step size",
        examples=[
            "transparency_range protein, 385, 415, 0.1, 0.05, increase, 1",
            "transparency_range ligand, 50, 60, 0.0, 0.2, increase, 2",
        ],
        tags=["animation", "transparency", "range", "step", "movie"],
        see_also=[
            "movie_transparency",
            "set_frame_transparency",
            "transparency_sequence",
        ],
    )

    # ------------------------------------------------------------------
    # movie_from_group
    # ------------------------------------------------------------------
    registry.register(
        "movie_from_group",
        movie_from_group,
        category=CATEGORY,
        description="Set up a movie that cycles through each object in a group",
        examples=[
            "movie_from_group my_group, 10",
            "movie_from_group proteins, 5",
        ],
        tags=["animation", "movie", "group", "scene"],
        see_also=["movie_transparency", "fade_in", "fade_out"],
    )

    # ------------------------------------------------------------------
    # Autocompletion
    # ------------------------------------------------------------------
    # Slot 0: selection for most commands
    for cmd_name in (
        "movie_transparency",
        "fade_in",
        "fade_out",
        "transparency_pulse",
        "suggest_transparency_type",
        "set_frame_transparency",
        "transparency_sequence",
        "transparency_range",
    ):
        autocomplete.register(cmd_name, 0, completers.object_name, "selection")

    # Slot 0 for movie_from_group: group name
    autocomplete.register("movie_from_group", 0, completers.group_name, "group")

    _tt = "transparency_type"
    # Transparency-type slot (varies by command signature)
    autocomplete.register("movie_transparency", 5, _TRANSPARENCY_TYPES, _tt)
    autocomplete.register("movie_transparency", 6, _DIRECTIONS, "direction")
    autocomplete.register("fade_in", 3, _TRANSPARENCY_TYPES, _tt)
    autocomplete.register("fade_out", 3, _TRANSPARENCY_TYPES, _tt)
    autocomplete.register("transparency_pulse", 5, _TRANSPARENCY_TYPES, _tt)
    autocomplete.register("set_frame_transparency", 3, _TRANSPARENCY_TYPES, _tt)
    autocomplete.register("transparency_sequence", 2, _TRANSPARENCY_TYPES, _tt)
    autocomplete.register("transparency_range", 5, _DIRECTIONS, "direction")
    autocomplete.register("transparency_range", 6, _TRANSPARENCY_TYPES, _tt)
