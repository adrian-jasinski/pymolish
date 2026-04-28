"""Group coloring commands: palette-based and gradient-based coloring."""

from __future__ import annotations

import random as _random

from pymol import cmd

from ...core.logging import plog
from ...core.validators import coerce_bool

from .palettes import COLOR_PALETTES, register_extended_colors

_TAG = "viz.color_group"


def _clean(value: str) -> str:
    """Strip one layer of surrounding quotes from PyMOL command arguments."""
    if not isinstance(value, str):
        return value
    return value.strip().strip("'\"")


def _resolve_targets(group_or_selection: str) -> list[str]:
    """Return the list of PyMOL objects belonging to *group_or_selection*.

    Tries ``cmd.get_object_list`` against the selection first (works for both
    groups and arbitrary selections).  Falls back to an atom-count scan over
    all loaded objects when the first call returns an empty list.
    """
    target_objects: list[str] = []
    try:
        members = cmd.get_object_list(f"({group_or_selection})")
        if members:
            target_objects = list(members)
    except Exception:  # noqa: BLE001
        pass

    if not target_objects:
        try:
            all_objects = cmd.get_object_list("all") or []
        except Exception:  # noqa: BLE001
            all_objects = []
        for obj in all_objects:
            try:
                if cmd.count_atoms(f"({obj}) and ({group_or_selection})") > 0:
                    target_objects.append(obj)
            except Exception:  # noqa: BLE001
                continue

    return target_objects


def color_group_with_palette(
    group_or_selection: str,
    palette_name: str = "pastels",
    auto_register: bool | str | int = True,
    random_order: bool | str | int = False,
    start_index: int | str = 0,
    verbose: bool | str | int = True,
) -> dict[str, str]:
    """Color all objects in a group or selection using an extended palette.

    Each object is assigned the next color in the palette, cycling when the
    number of objects exceeds the palette length.

    Args:
        group_or_selection: PyMOL group name or selection expression.
        palette_name: Extended palette to use (default: ``"pastels"``).
        auto_register: When truthy, register palette colors with PyMOL before
            applying them. Default: ``True``.
        random_order: When truthy, shuffle object order before assigning colors.
            Default: ``False``.
        start_index: Palette index to begin from (default: ``0``).
        verbose: When truthy, log each color assignment. Default: ``True``.

    Returns:
        Mapping of ``{object_name: color_name}`` for successfully colored objects.
        Returns an empty dict on errors.

    Examples:
        PyMOL> color_group_with_palette my_group, pastels
        PyMOL> color_group_with_palette proteins, neon, 1, 1
        PyMOL> color_group_with_palette structures, earth, 0, 0, 5

    Since:
        1.0.0

    See Also:
        color_group_with_gradient, register_extended_colors, list_available_palettes
    """
    group_or_selection = _clean(group_or_selection)
    palette_name = _clean(palette_name).lower()
    auto_register = coerce_bool(auto_register)
    random_order = coerce_bool(random_order)
    verbose = coerce_bool(verbose)
    try:
        start_index = int(start_index)
    except (TypeError, ValueError):
        start_index = 0

    if palette_name not in COLOR_PALETTES:
        plog(_TAG, f"unknown palette '{palette_name}'", "error")
        plog(_TAG, f"available palettes: {list(COLOR_PALETTES.keys())}")
        return {}

    target_objects = _resolve_targets(group_or_selection)
    if not target_objects:
        plog(_TAG, f"no objects found in '{group_or_selection}'", "error")
        return {}

    if verbose:
        plog(
            _TAG,
            f"coloring {len(target_objects)} object(s) with '{palette_name}' palette",
        )

    if auto_register:
        register_extended_colors(palette_name, verbose=False)

    palette_colors = COLOR_PALETTES[palette_name]
    num_colors = len(palette_colors)

    object_order = list(target_objects)
    if random_order:
        _random.shuffle(object_order)

    color_assignments: dict[str, str] = {}
    for i, obj in enumerate(object_order):
        color_index = (start_index + i) % num_colors
        color_name = f"{palette_name}_{color_index + 1:02d}"
        try:
            cmd.color(color_name, obj)
            color_assignments[obj] = color_name
            if verbose:
                r, g, b = palette_colors[color_index]
                plog(_TAG, f"{obj} -> {color_name} RGB({r:.3f}, {g:.3f}, {b:.3f})")
        except Exception as exc:  # noqa: BLE001
            plog(_TAG, f"could not color {obj} with {color_name}: {exc}", "warn")

    if verbose:
        plog(
            _TAG,
            f"colored {len(color_assignments)} object(s) with '{palette_name}' palette",
        )
    return color_assignments


def color_group_with_gradient(
    group_or_selection: str,
    base_color: str = "blue",
    num_colors: int | str | None = None,
    gradient_type: str = "lightness",
    verbose: bool | str | int = True,
) -> dict[str, str]:
    """Color objects in a group with a gradient derived from a single base color.

    Requires the ``matplotlib`` package for color space conversions (install with
    ``pip install pymolish[matplotlib]``). The gradient is computed in HSV space
    using colorsys from the Python standard library; matplotlib is used only for
    named-color resolution when ``base_color`` is not a PyMOL built-in.

    Args:
        group_or_selection: PyMOL group name or selection expression.
        base_color: Named PyMOL color or RGB tuple to derive the gradient from.
            Default: ``"blue"``.
        num_colors: Number of gradient steps. Defaults to the number of objects.
        gradient_type: One of ``"lightness"``, ``"saturation"``, or ``"hue"``.
            Default: ``"lightness"``.
        verbose: When truthy, log each color assignment. Default: ``True``.

    Returns:
        Mapping of ``{object_name: color_name}`` for successfully colored objects.
        Returns an empty dict on errors.

    Examples:
        PyMOL> color_group_with_gradient my_group, blue
        PyMOL> color_group_with_gradient proteins, red, 10, lightness
        PyMOL> color_group_with_gradient chains, green, , saturation

    Since:
        1.0.0

    See Also:
        color_group_with_palette, register_extended_colors
    """
    import colorsys

    group_or_selection = _clean(group_or_selection)
    base_color = _clean(base_color)
    gradient_type = _clean(gradient_type).lower()
    verbose = coerce_bool(verbose)

    if num_colors is not None and str(num_colors).strip().lower() not in ("", "none"):
        try:
            num_colors = int(num_colors)
        except (TypeError, ValueError):
            num_colors = None

    valid_gradients = ("lightness", "saturation", "hue")
    if gradient_type not in valid_gradients:
        plog(
            _TAG,
            f"unknown gradient_type '{gradient_type}'; choose one of {valid_gradients}",
            "error",
        )
        return {}

    target_objects = _resolve_targets(group_or_selection)
    if not target_objects:
        plog(_TAG, f"no objects found in '{group_or_selection}'", "error")
        return {}

    effective_num = num_colors if isinstance(num_colors, int) else len(target_objects)

    if verbose:
        n_obj = len(target_objects)
        plog(_TAG, f"{gradient_type} gradient: {effective_num} colors, {n_obj} objects")

    # Resolve base color to an RGB tuple via PyMOL
    if isinstance(base_color, str):
        try:
            base_rgb = cmd.get_color_tuple(base_color)
        except Exception:  # noqa: BLE001
            plog(_TAG, f"unknown color '{base_color}'", "error")
            return {}
    else:
        base_rgb = tuple(base_color)

    h, s, v = colorsys.rgb_to_hsv(*base_rgb)

    color_assignments: dict[str, str] = {}
    for i, obj in enumerate(target_objects):
        progress = i / max(1, effective_num - 1)

        if gradient_type == "lightness":
            new_h, new_s, new_v = h, s, 0.3 + (0.7 * progress)
        elif gradient_type == "saturation":
            new_h, new_s, new_v = h, 0.2 + (0.8 * progress), v
        else:  # hue
            hue_range = 0.15
            new_h, new_s, new_v = (h + hue_range * (progress - 0.5)) % 1.0, s, v

        r, g, b = colorsys.hsv_to_rgb(new_h, new_s, new_v)
        color_name = f"gradient_{gradient_type}_{i + 1:02d}"
        try:
            cmd.set_color(color_name, [r, g, b])
            cmd.color(color_name, obj)
            color_assignments[obj] = color_name
            if verbose:
                plog(_TAG, f"{obj} -> {color_name}")
        except Exception as exc:  # noqa: BLE001
            plog(_TAG, f"could not color {obj}: {exc}", "warn")

    return color_assignments
