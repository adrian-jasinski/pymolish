"""Palette data and registration helpers for the Visualization category.

All palette constants live here so that ``color_group`` and ``color_ss`` can
import them without creating circular dependencies.
"""

from __future__ import annotations

from pymol import cmd

from ...core.logging import plog

_TAG = "viz.palettes"

# ---------------------------------------------------------------------------
# Color palette data
# ---------------------------------------------------------------------------

PASTELS: list[tuple[float, float, float]] = [
    (1.0, 0.8, 0.8),
    (0.8, 1.0, 0.8),
    (0.8, 0.8, 1.0),
    (1.0, 1.0, 0.8),
    (1.0, 0.8, 1.0),
    (0.8, 1.0, 1.0),
    (1.0, 0.9, 0.8),
    (0.9, 0.8, 1.0),
    (0.8, 1.0, 0.9),
    (1.0, 0.8, 0.9),
    (0.9, 0.9, 0.8),
    (0.8, 0.9, 1.0),
    (0.95, 0.8, 0.85),
    (0.85, 0.95, 0.85),
    (0.9, 0.85, 1.0),
    (1.0, 0.9, 0.9),
    (0.8, 0.95, 0.95),
    (0.95, 0.95, 0.8),
    (0.9, 0.8, 0.95),
    (0.85, 1.0, 0.85),
    (1.0, 0.85, 0.8),
    (0.8, 0.85, 0.95),
    (0.95, 1.0, 0.8),
    (0.85, 0.8, 1.0),
    (1.0, 0.95, 0.85),
]

NEON: list[tuple[float, float, float]] = [
    (1.0, 0.0, 1.0),
    (0.0, 1.0, 0.0),
    (0.0, 1.0, 1.0),
    (1.0, 1.0, 0.0),
    (1.0, 0.3, 0.0),
    (0.5, 0.0, 1.0),
    (1.0, 0.0, 0.5),
    (0.0, 0.8, 1.0),
    (0.8, 1.0, 0.0),
    (1.0, 0.0, 0.0),
    (0.0, 0.5, 1.0),
    (1.0, 0.8, 0.0),
    (0.6, 0.0, 1.0),
    (1.0, 0.0, 0.8),
    (0.0, 1.0, 0.4),
    (1.0, 0.5, 0.0),
    (0.2, 0.0, 1.0),
    (1.0, 0.2, 0.8),
    (0.4, 1.0, 0.0),
    (1.0, 0.7, 0.0),
    (0.0, 0.6, 1.0),
    (0.9, 0.0, 1.0),
    (0.6, 1.0, 0.0),
    (1.0, 0.4, 0.0),
    (0.0, 0.9, 1.0),
]

EARTH: list[tuple[float, float, float]] = [
    (0.55, 0.27, 0.07),
    (0.36, 0.25, 0.20),
    (0.80, 0.52, 0.25),
    (0.13, 0.55, 0.13),
    (0.54, 0.27, 0.07),
    (0.50, 0.50, 0.00),
    (0.72, 0.53, 0.04),
    (0.40, 0.26, 0.13),
    (0.29, 0.51, 0.16),
    (0.65, 0.43, 0.28),
    (0.59, 0.29, 0.00),
    (0.35, 0.58, 0.00),
    (0.69, 0.51, 0.38),
    (0.42, 0.42, 0.18),
    (0.77, 0.38, 0.06),
    (0.25, 0.38, 0.00),
    (0.64, 0.16, 0.16),
    (0.56, 0.56, 0.33),
    (0.80, 0.36, 0.00),
    (0.33, 0.42, 0.18),
    (0.72, 0.45, 0.20),
    (0.20, 0.29, 0.09),
    (0.61, 0.35, 0.25),
    (0.45, 0.45, 0.27),
    (0.83, 0.53, 0.10),
]

OCEAN: list[tuple[float, float, float]] = [
    (0.00, 0.50, 1.00),
    (0.00, 0.75, 0.75),
    (0.25, 0.88, 0.82),
    (0.00, 0.20, 0.40),
    (0.53, 0.81, 0.92),
    (0.00, 0.39, 0.39),
    (0.40, 0.80, 1.00),
    (0.00, 0.27, 0.55),
    (0.69, 0.88, 0.90),
    (0.00, 0.46, 0.65),
    (0.12, 0.56, 0.93),
    (0.00, 0.42, 0.58),
    (0.27, 0.51, 0.71),
    (0.67, 0.85, 0.90),
    (0.00, 0.32, 0.54),
    (0.44, 0.74, 0.89),
    (0.00, 0.62, 0.76),
    (0.28, 0.24, 0.55),
    (0.73, 0.88, 0.98),
    (0.25, 0.41, 0.88),
    (0.00, 0.35, 0.67),
    (0.39, 0.58, 0.93),
    (0.06, 0.32, 0.73),
    (0.50, 0.78, 1.00),
    (0.00, 0.27, 0.42),
]

WARM: list[tuple[float, float, float]] = [
    (1.0, 0.27, 0.00),
    (1.0, 0.65, 0.00),
    (1.0, 0.84, 0.00),
    (0.86, 0.08, 0.24),
    (1.0, 0.50, 0.31),
    (1.0, 0.71, 0.76),
    (0.72, 0.11, 0.11),
    (1.0, 0.39, 0.28),
    (1.0, 0.75, 0.80),
    (0.98, 0.50, 0.45),
    (1.0, 0.55, 0.00),
    (0.94, 0.00, 0.31),
    (1.0, 0.41, 0.38),
    (0.80, 0.36, 0.36),
    (1.0, 0.89, 0.71),
    (0.93, 0.51, 0.93),
    (1.0, 0.63, 0.48),
    (0.85, 0.44, 0.84),
    (1.0, 0.92, 0.80),
    (0.96, 0.64, 0.38),
    (1.0, 0.20, 0.70),
    (0.93, 0.46, 0.00),
    (1.0, 0.83, 0.61),
    (0.87, 0.72, 0.53),
    (1.0, 0.98, 0.94),
]

COOL: list[tuple[float, float, float]] = [
    (0.25, 0.88, 0.82),
    (0.53, 0.81, 0.92),
    (0.48, 0.41, 0.93),
    (0.30, 0.69, 0.31),
    (0.00, 0.50, 0.50),
    (0.42, 0.35, 0.80),
    (0.50, 1.00, 0.83),
    (0.68, 0.85, 0.90),
    (0.22, 0.56, 0.24),
    (0.69, 0.77, 0.87),
    (0.40, 0.80, 0.67),
    (0.60, 0.80, 1.00),
    (0.18, 0.31, 0.31),
    (0.56, 0.93, 0.56),
    (0.73, 0.33, 0.83),
    (0.44, 0.50, 0.56),
    (0.24, 0.70, 0.44),
    (0.82, 0.71, 0.55),
    (0.20, 0.80, 0.60),
    (0.75, 0.75, 0.75),
    (0.00, 0.80, 0.80),
    (0.86, 0.44, 0.58),
    (0.94, 0.97, 1.00),
    (0.56, 0.74, 0.56),
    (0.88, 0.94, 0.96),
]

COLOR_PALETTES: dict[str, list[tuple[float, float, float]]] = {
    "pastels": PASTELS,
    "neon": NEON,
    "earth": EARTH,
    "ocean": OCEAN,
    "warm": WARM,
    "cool": COOL,
}

PALETTE_DESCRIPTIONS: dict[str, str] = {
    "pastels": "Soft, muted colors perfect for gentle visualizations",
    "neon": "Bright, electric colors for high-contrast displays",
    "earth": "Natural, earthy tones ideal for biological structures",
    "ocean": "Blue and aquatic colors for cool presentations",
    "warm": "Red, orange, yellow spectrum for highlighting regions",
    "cool": "Blue, green, purple spectrum for professional presentations",
}

# ---------------------------------------------------------------------------
# Secondary-structure palette data
# ---------------------------------------------------------------------------

CARTOON_PALETTES: dict[str, dict[str, str]] = {
    "ard": {
        "helix": "ard_purple",
        "sheet": "ard_yellow",
        "loop": "ard_light_violet",
        "description": "Purple helices, yellow sheets, light violet loops",
    },
    "ard_green": {
        "helix": "ard_green",
        "sheet": "wheat",
        "loop": "palegreen",
        "description": "Green helices, wheat sheets, pale green loops",
    },
    "ocean_depths": {
        "helix": "marine",
        "sheet": "orange",
        "loop": "lightblue",
        "description": "Marine blue helices, orange sheets, light blue loops",
    },
    "sunset": {
        "helix": "red",
        "sheet": "cyan",
        "loop": "salmon",
        "description": "Red helices, cyan sheets, salmon loops",
    },
    "forest": {
        "helix": "forest",
        "sheet": "yellow",
        "loop": "lime",
        "description": "Forest green helices, yellow sheets, lime loops",
    },
    "royal": {
        "helix": "blue",
        "sheet": "gold",
        "loop": "lightblue",
        "description": "Blue helices, gold sheets, light blue loops",
    },
    "autumn": {
        "helix": "brown",
        "sheet": "cyan",
        "loop": "lightorange",
        "description": "Brown helices, cyan sheets, light orange loops",
    },
    "electric": {
        "helix": "magenta",
        "sheet": "yellow",
        "loop": "lightmagenta",
        "description": "Magenta helices, yellow sheets, light magenta loops",
    },
    "monochrome": {
        "helix": "black",
        "sheet": "white",
        "loop": "gray",
        "description": "Black helices, white sheets, gray loops",
    },
    "candy": {
        "helix": "hotpink",
        "sheet": "lime",
        "loop": "lightpink",
        "description": "Hot pink helices, lime sheets, light pink loops",
    },
}

# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------


def register_extended_colors(
    palette_name: str | None = None,
    verbose: bool | str | int = True,
) -> int:
    """Register extended color palettes with PyMOL's color system.

    Calls ``cmd.set_color`` for every RGB entry in the selected palette(s),
    making them available for use as named colors in all PyMOL commands.

    Args:
        palette_name: Name of a specific palette to register (e.g. ``"pastels"``).
            When omitted or empty, all palettes are registered.
        verbose: When truthy, log each registered color name. Default: ``True``.

    Returns:
        Number of colors successfully registered.

    Examples:
        PyMOL> register_extended_colors
        PyMOL> register_extended_colors pastels
        PyMOL> register_extended_colors neon, 0

    Since:
        1.0.0

    See Also:
        list_available_palettes, color_group_with_palette
    """
    from ...core.validators import coerce_bool

    verbose = coerce_bool(verbose)

    if palette_name and palette_name.strip():
        key = palette_name.strip().lower()
        if key not in COLOR_PALETTES:
            plog(_TAG, f"unknown palette '{key}'", "error")
            plog(_TAG, f"available palettes: {list(COLOR_PALETTES.keys())}")
            return 0
        palettes_to_register = [key]
    else:
        palettes_to_register = list(COLOR_PALETTES.keys())

    registered = 0
    for palette in palettes_to_register:
        for i, (r, g, b) in enumerate(COLOR_PALETTES[palette]):
            color_name = f"{palette}_{i + 1:02d}"
            try:
                cmd.set_color(color_name, [r, g, b])
                registered += 1
                if verbose:
                    plog(
                        _TAG,
                        f"registered '{color_name}': RGB({r:.3f}, {g:.3f}, {b:.3f})",
                    )
            except Exception as exc:  # noqa: BLE001
                plog(_TAG, f"could not register '{color_name}': {exc}", "warn")

    if verbose:
        n = len(palettes_to_register)
        plog(_TAG, f"registered {registered} color(s) from {n} palette(s)")
    return registered


def list_available_palettes() -> list[str]:
    """Print all available color palettes with descriptions and color counts.

    Returns:
        List of palette names.

    Examples:
        PyMOL> list_available_palettes

    Since:
        1.0.0

    See Also:
        register_extended_colors, color_group_with_palette
    """
    plog(_TAG, "available color palettes:")
    for name, colors in COLOR_PALETTES.items():
        description = PALETTE_DESCRIPTIONS.get(name, "No description")
        preview = ", ".join(f"RGB({r:.2f},{g:.2f},{b:.2f})" for r, g, b in colors[:3])
        plog(_TAG, f"  {name}: {len(colors)} colors — {description}")
        plog(_TAG, f"    preview: {preview}, ... ({len(colors)} total)")
    return list(COLOR_PALETTES.keys())
