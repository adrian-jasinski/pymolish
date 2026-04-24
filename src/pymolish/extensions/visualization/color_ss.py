"""Secondary-structure coloring commands."""

from __future__ import annotations

from pymol import cmd

from pymolish.core.logging import plog
from pymolish.core.validators import coerce_bool

from .palettes import CARTOON_PALETTES

_TAG = "viz.color_ss"


def _clean(value: str) -> str:
    """Strip one layer of surrounding quotes from PyMOL command arguments."""
    if not isinstance(value, str):
        return value
    return value.strip().strip("'\"")


def color_secondary_structure(
    target_object: str,
    palette: str = "ard",
    verbose: bool | str | int = True,
) -> dict[str, object]:
    """Color secondary structure elements using a predefined palette.

    Applies distinct colors to helices (``ss h``), beta sheets (``ss s``),
    and loops/coils (``ss l+''``) within the specified PyMOL object.

    Args:
        target_object: Name of the PyMOL object to color.
        palette: Secondary-structure palette name (default: ``"ard"``).
            Use :func:`list_cartoon_palettes` to see available options.
        verbose: When truthy, log coloring details. Default: ``True``.

    Returns:
        Summary dict with keys ``palette``, ``description``, and per-element
        sub-dicts ``{color, atoms}`` for helices, sheets, and loops.
        Returns an empty dict when the object is not found or coloring fails.

    Examples:
        PyMOL> color_secondary_structure protein
        PyMOL> color_secondary_structure my_structure, ard_green
        PyMOL> color_secondary_structure complex, ocean_depths, 0

    Since:
        1.0.0

    See Also:
        list_cartoon_palettes, color_group_with_palette
    """
    target_object = _clean(target_object)
    palette = _clean(palette)
    verbose = coerce_bool(verbose)

    if palette not in CARTOON_PALETTES:
        plog(_TAG, f"unknown palette '{palette}'", "error")
        plog(_TAG, f"available palettes: {list(CARTOON_PALETTES.keys())}")
        return {}

    palette_info = CARTOON_PALETTES[palette]
    helix_color = palette_info["helix"]
    sheet_color = palette_info["sheet"]
    loop_color = palette_info["loop"]

    if verbose:
        plog(_TAG, f"using '{palette}' palette: {palette_info['description']}")
        plog(_TAG, f"coloring secondary structure of '{target_object}'")

    objects = cmd.get_object_list() or []
    if target_object not in objects:
        plog(_TAG, f"object '{target_object}' not found", "error")
        plog(_TAG, f"available objects: {objects}")
        return {}

    color_summary: dict[str, object] = {
        "palette": palette,
        "description": palette_info["description"],
    }

    try:
        helix_sel = f"({target_object}) and ss h"
        helix_count = cmd.count_atoms(helix_sel)
        if helix_count > 0:
            cmd.color(helix_color, helix_sel)
            color_summary["helices"] = {"color": helix_color, "atoms": helix_count}
            if verbose:
                plog(_TAG, f"helices -> {helix_color} ({helix_count} atoms)")

        sheet_sel = f"({target_object}) and ss s"
        sheet_count = cmd.count_atoms(sheet_sel)
        if sheet_count > 0:
            cmd.color(sheet_color, sheet_sel)
            color_summary["sheets"] = {"color": sheet_color, "atoms": sheet_count}
            if verbose:
                plog(_TAG, f"beta sheets -> {sheet_color} ({sheet_count} atoms)")

        loop_sel = f"({target_object}) and ss l+''"
        loop_count = cmd.count_atoms(loop_sel)
        if loop_count > 0:
            cmd.color(loop_color, loop_sel)
            color_summary["loops"] = {"color": loop_color, "atoms": loop_count}
            if verbose:
                plog(_TAG, f"loops/coils -> {loop_color} ({loop_count} atoms)")

        if verbose:
            element_counts = [
                info["atoms"]
                for key, info in color_summary.items()
                if isinstance(info, dict) and "atoms" in info
            ]
            n_types = len(element_counts)
            total = sum(element_counts)
            msg = f"colored {total} atoms across {n_types} secondary-structure types"
            plog(_TAG, msg)

    except Exception as exc:  # noqa: BLE001
        plog(_TAG, f"failed to color secondary structure: {exc}", "error")
        return {}

    return color_summary


def list_cartoon_palettes() -> list[str]:
    """Print all available secondary-structure color palettes.

    Returns:
        List of palette names.

    Examples:
        PyMOL> list_cartoon_palettes

    Since:
        1.0.0

    See Also:
        color_secondary_structure
    """
    plog(_TAG, "available secondary-structure palettes:")
    for name, info in CARTOON_PALETTES.items():
        plog(_TAG, f"  {name}: {info['description']}")
        h, s, lo = info["helix"], info["sheet"], info["loop"]
        plog(_TAG, f"    helix={h!r}  sheet={s!r}  loop={lo!r}")
    return list(CARTOON_PALETTES.keys())
