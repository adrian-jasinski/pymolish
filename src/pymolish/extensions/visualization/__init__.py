"""Color and visualization extensions: palettes, color_group, color_ss."""

from __future__ import annotations

from pymolish.core.autocompletion import AutocompletionRegistry
from pymolish.core.registry import CommandRegistry
from pymolish.core.types import Category

CATEGORY = Category.VISUALIZATION


def __init_plugin__(app: object | None = None) -> None:
    """Register visualization commands and their autocompletions."""
    from .color_group import (
        color_group_with_gradient,
        color_group_with_palette,
    )
    from .color_ss import color_secondary_structure, list_cartoon_palettes
    from .palettes import (
        CARTOON_PALETTES,
        COLOR_PALETTES,
        list_available_palettes,
        register_extended_colors,
    )

    registry = CommandRegistry.instance()
    autocomplete = AutocompletionRegistry.instance()
    completers = autocomplete.completers

    # ------------------------------------------------------------------
    # Local completers
    # ------------------------------------------------------------------

    def _palette_completer(token: str) -> list[str]:
        return [p for p in COLOR_PALETTES if p.startswith(token.lower())]

    def _cartoon_palette_completer(token: str) -> list[str]:
        return [p for p in CARTOON_PALETTES if p.startswith(token.lower())]

    _gradient_types = ["lightness", "saturation", "hue"]

    def _gradient_completer(token: str) -> list[str]:
        return [g for g in _gradient_types if g.startswith(token.lower())]

    # ------------------------------------------------------------------
    # palettes.py commands
    # ------------------------------------------------------------------

    registry.register(
        "register_extended_colors",
        register_extended_colors,
        category=CATEGORY,
        description="Register extended color palettes with PyMOL's color system",
        examples=[
            "register_extended_colors",
            "register_extended_colors pastels",
            "register_extended_colors neon, 0",
        ],
        tags=["color", "palette", "register"],
        see_also=["list_available_palettes", "color_group_with_palette"],
    )

    registry.register(
        "list_available_palettes",
        list_available_palettes,
        category=CATEGORY,
        description="List all available color palettes with descriptions",
        examples=[
            "list_available_palettes",
        ],
        tags=["color", "palette", "list"],
        see_also=["register_extended_colors", "color_group_with_palette"],
    )

    # ------------------------------------------------------------------
    # color_group.py commands
    # ------------------------------------------------------------------

    registry.register(
        "color_group_with_palette",
        color_group_with_palette,
        category=CATEGORY,
        description="Color objects in a group or selection with an extended palette",
        examples=[
            "color_group_with_palette my_group, pastels",
            "color_group_with_palette proteins, neon, 1, 1",
            "color_group_with_palette structures, earth, 0, 0, 5",
        ],
        tags=["color", "palette", "group", "visualization"],
        see_also=[
            "color_group_with_gradient",
            "register_extended_colors",
            "list_available_palettes",
        ],
    )

    registry.register(
        "color_group_with_gradient",
        color_group_with_gradient,
        category=CATEGORY,
        description=(
            "Color objects in a group with a gradient derived from a single base color"
        ),
        examples=[
            "color_group_with_gradient my_group, blue",
            "color_group_with_gradient proteins, red, 10, lightness",
            "color_group_with_gradient chains, green, , saturation",
        ],
        tags=["color", "gradient", "group", "visualization"],
        see_also=["color_group_with_palette", "register_extended_colors"],
    )

    # ------------------------------------------------------------------
    # color_ss.py commands
    # ------------------------------------------------------------------

    registry.register(
        "color_secondary_structure",
        color_secondary_structure,
        category=CATEGORY,
        description=("Color secondary structure elements using a predefined palette"),
        examples=[
            "color_secondary_structure protein",
            "color_secondary_structure my_structure, ard_green",
            "color_secondary_structure complex, ocean_depths, 0",
        ],
        tags=["color", "secondary structure", "cartoon", "visualization"],
        see_also=["list_cartoon_palettes", "color_group_with_palette"],
    )

    registry.register(
        "list_cartoon_palettes",
        list_cartoon_palettes,
        category=CATEGORY,
        description="List all available secondary-structure color palettes",
        examples=[
            "list_cartoon_palettes",
        ],
        tags=["color", "secondary structure", "cartoon", "list"],
        see_also=["color_secondary_structure"],
    )

    # ------------------------------------------------------------------
    # Autocompletion
    # ------------------------------------------------------------------

    autocomplete.register("register_extended_colors", 0, _palette_completer, "palette")

    autocomplete.register(
        "color_group_with_palette", 0, completers.object_name, "group_or_selection"
    )
    autocomplete.register(
        "color_group_with_palette", 1, _palette_completer, "palette_name"
    )

    autocomplete.register(
        "color_group_with_gradient", 0, completers.object_name, "group_or_selection"
    )
    autocomplete.register(
        "color_group_with_gradient", 3, _gradient_completer, "gradient_type"
    )

    autocomplete.register(
        "color_secondary_structure", 0, completers.object_name, "target_object"
    )
    autocomplete.register(
        "color_secondary_structure", 1, _cartoon_palette_completer, "palette"
    )

    autocomplete.register(
        "list_cartoon_palettes", 0, _cartoon_palette_completer, "palette"
    )
