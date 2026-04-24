# Visualization

_6 command(s). Generated from the command registry — do not edit by hand._

## Commands in this category

- [`color_group_with_gradient`](#color_group_with_gradient) — Color objects in a group with a gradient derived from a single base color
- [`color_group_with_palette`](#color_group_with_palette) — Color objects in a group or selection with an extended palette
- [`color_secondary_structure`](#color_secondary_structure) — Color secondary structure elements using a predefined palette
- [`list_available_palettes`](#list_available_palettes) — List all available color palettes with descriptions
- [`list_cartoon_palettes`](#list_cartoon_palettes) — List all available secondary-structure color palettes
- [`register_extended_colors`](#register_extended_colors) — Register extended color palettes with PyMOL's color system

---

### `color_group_with_gradient`

Color objects in a group with a gradient derived from a single base color

- **Usage:** `color_group_with_gradient <group_or_selection> [base_color='blue'] [num_colors=None] [gradient_type='lightness'] [verbose=True]`
- **Since:** 1.0.0
- **Tags:** `color`, `gradient`, `group`, `visualization`
- **See also:** `color_group_with_palette`, `register_extended_colors`

**Examples:**

```
color_group_with_gradient my_group, blue
color_group_with_gradient proteins, red, 10, lightness
color_group_with_gradient chains, green, , saturation
```

<details><summary>Full docstring</summary>

```
Color objects in a group with a gradient derived from a single base color.

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
```

</details>

### `color_group_with_palette`

Color objects in a group or selection with an extended palette

- **Usage:** `color_group_with_palette <group_or_selection> [palette_name='pastels'] [auto_register=True] [random_order=False] [start_index=0] [verbose=True]`
- **Since:** 1.0.0
- **Tags:** `color`, `palette`, `group`, `visualization`
- **See also:** `color_group_with_gradient`, `register_extended_colors`, `list_available_palettes`

**Examples:**

```
color_group_with_palette my_group, pastels
color_group_with_palette proteins, neon, 1, 1
color_group_with_palette structures, earth, 0, 0, 5
```

<details><summary>Full docstring</summary>

```
Color all objects in a group or selection using an extended palette.

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
```

</details>

### `color_secondary_structure`

Color secondary structure elements using a predefined palette

- **Usage:** `color_secondary_structure <target_object> [palette='ard'] [verbose=True]`
- **Since:** 1.0.0
- **Tags:** `color`, `secondary structure`, `cartoon`, `visualization`
- **See also:** `list_cartoon_palettes`, `color_group_with_palette`

**Examples:**

```
color_secondary_structure protein
color_secondary_structure my_structure, ard_green
color_secondary_structure complex, ocean_depths, 0
```

<details><summary>Full docstring</summary>

```
Color secondary structure elements using a predefined palette.

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
```

</details>

### `list_available_palettes`

List all available color palettes with descriptions

- **Usage:** `list_available_palettes`
- **Since:** 1.0.0
- **Tags:** `color`, `palette`, `list`
- **See also:** `register_extended_colors`, `color_group_with_palette`

**Examples:**

```
list_available_palettes
```

<details><summary>Full docstring</summary>

```
Print all available color palettes with descriptions and color counts.

Returns:
    List of palette names.

Examples:
    PyMOL> list_available_palettes

Since:
    1.0.0

See Also:
    register_extended_colors, color_group_with_palette
```

</details>

### `list_cartoon_palettes`

List all available secondary-structure color palettes

- **Usage:** `list_cartoon_palettes`
- **Since:** 1.0.0
- **Tags:** `color`, `secondary structure`, `cartoon`, `list`
- **See also:** `color_secondary_structure`

**Examples:**

```
list_cartoon_palettes
```

<details><summary>Full docstring</summary>

```
Print all available secondary-structure color palettes.

Returns:
    List of palette names.

Examples:
    PyMOL> list_cartoon_palettes

Since:
    1.0.0

See Also:
    color_secondary_structure
```

</details>

### `register_extended_colors`

Register extended color palettes with PyMOL's color system

- **Usage:** `register_extended_colors [palette_name=None] [verbose=True]`
- **Since:** 1.0.0
- **Tags:** `color`, `palette`, `register`
- **See also:** `list_available_palettes`, `color_group_with_palette`

**Examples:**

```
register_extended_colors
register_extended_colors pastels
register_extended_colors neon, 0
```

<details><summary>Full docstring</summary>

```
Register extended color palettes with PyMOL's color system.

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
```

</details>
