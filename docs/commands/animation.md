# Animation

_9 command(s). Generated from the command registry — do not edit by hand._

## Commands in this category

- [`fade_in`](#fade_in) — Fade objects in (decrease transparency from 1.0 to 0.0)
- [`fade_out`](#fade_out) — Fade objects out (increase transparency from 0.0 to 1.0)
- [`movie_from_group`](#movie_from_group) — Set up a movie that cycles through each object in a group
- [`movie_transparency`](#movie_transparency) — Animate transparency linearly over a frame range
- [`set_frame_transparency`](#set_frame_transparency) — Set transparency for a single specific frame
- [`suggest_transparency_type`](#suggest_transparency_type) — Suggest the best transparency type for a selection
- [`transparency_pulse`](#transparency_pulse) — Create a pulsing transparency effect over multiple cycles
- [`transparency_range`](#transparency_range) — Set transparency across a frame range with a fixed step size
- [`transparency_sequence`](#transparency_sequence) — Set transparency for multiple frames via frame:value pairs

---

### `fade_in`

Fade objects in (decrease transparency from 1.0 to 0.0)

- **Usage:** `fade_in [selection='all'] [start_frame=1] [end_frame=30] [transparency_type=0]`
- **Since:** 1.0.0
- **Tags:** `animation`, `fade`, `transparency`, `movie`
- **See also:** `fade_out`, `movie_transparency`

**Examples:**

```
fade_in protein, 1, 30
fade_in ligand, 10, 50, 1
```

<details><summary>Full docstring</summary>

```
Fade objects in (decrease transparency from 1.0 to 0.0).

Convenience wrapper around :func:`movie_transparency`.

Args:
    selection: PyMOL selection (default: ``"all"``).
    start_frame: First frame (default: ``1``).
    end_frame: Last frame (default: ``30``).
    transparency_type: Transparency setting index 0–3 (default: ``0``).

Returns:
    Number of frames successfully processed.

Examples:
    PyMOL> fade_in protein, 1, 30
    PyMOL> fade_in ligand, 10, 50, 1

Since:
    1.0.0

See Also:
    fade_out, movie_transparency
```

</details>

### `fade_out`

Fade objects out (increase transparency from 0.0 to 1.0)

- **Usage:** `fade_out [selection='all'] [start_frame=1] [end_frame=30] [transparency_type=0]`
- **Since:** 1.0.0
- **Tags:** `animation`, `fade`, `transparency`, `movie`
- **See also:** `fade_in`, `movie_transparency`

**Examples:**

```
fade_out protein, 1, 30
fade_out complex, 20, 60, 1
```

<details><summary>Full docstring</summary>

```
Fade objects out (increase transparency from 0.0 to 1.0).

Convenience wrapper around :func:`movie_transparency`.

Args:
    selection: PyMOL selection (default: ``"all"``).
    start_frame: First frame (default: ``1``).
    end_frame: Last frame (default: ``30``).
    transparency_type: Transparency setting index 0–3 (default: ``0``).

Returns:
    Number of frames successfully processed.

Examples:
    PyMOL> fade_out protein, 1, 30
    PyMOL> fade_out complex, 20, 60, 1

Since:
    1.0.0

See Also:
    fade_in, movie_transparency
```

</details>

### `movie_from_group`

Set up a movie that cycles through each object in a group

- **Usage:** `movie_from_group <group_name> [frames_per_object=10]`
- **Since:** 1.0.0
- **Tags:** `animation`, `movie`, `group`, `scene`
- **See also:** `movie_transparency`, `fade_in`, `fade_out`

**Examples:**

```
movie_from_group my_group, 10
movie_from_group proteins, 5
```

<details><summary>Full docstring</summary>

```
Set up a PyMOL movie that cycles through each object in a group.

Creates one scene per group member (only that member visible at a time),
sets the movie length to ``num_objects * frames_per_object``, and stores
``mview`` keyframes so each scene appears at the correct frame with
interpolation.

Args:
    group_name: Name of the PyMOL group containing the objects to cycle.
    frames_per_object: Number of movie frames allocated to each object
        (default: ``10``).

Returns:
    Total number of frames in the created movie (``0`` on failure).

Examples:
    PyMOL> movie_from_group my_group, 10
    PyMOL> movie_from_group proteins, 5

Since:
    1.0.0

See Also:
    movie_transparency, fade_in, fade_out
```

</details>

### `movie_transparency`

Animate transparency linearly over a frame range

- **Usage:** `movie_transparency [selection='all'] [start_frame=1] [end_frame=30] [start_transparency=0.0] [end_transparency=1.0] [transparency_type=0] [direction='increase']`
- **Since:** 1.0.0
- **Tags:** `animation`, `transparency`, `movie`, `fade`
- **See also:** `fade_in`, `fade_out`, `transparency_pulse`, `set_frame_transparency`

**Examples:**

```
movie_transparency protein, 10, 50, 0.0, 1.0, 1
movie_transparency ligand, 1, 100, 0.5, 0.0, 2, decrease
movie_transparency all, 1, 30
```

<details><summary>Full docstring</summary>

```
Animate transparency over a frame range in a PyMOL movie.

Sets a per-frame ``mdo`` command that linearly interpolates between
*start_transparency* and *end_transparency* over frames
*start_frame*–*end_frame*.

Args:
    selection: PyMOL selection (default: ``"all"``).
    start_frame: First frame of the animation (default: ``1``).
    end_frame: Last frame of the animation (default: ``30``).
    start_transparency: Starting transparency value 0.0–1.0 (default: ``0.0``).
    end_transparency: Ending transparency value 0.0–1.0 (default: ``1.0``).
    transparency_type: Transparency setting index (default: ``0``).
        ``0`` = ``transparency`` (surface),
        ``1`` = ``cartoon_transparency``,
        ``2`` = ``sphere_transparency``,
        ``3`` = ``cgo_transparency``.
    direction: ``"increase"`` or ``"decrease"`` (default: ``"increase"``).
        When ``"decrease"``, start and end values are swapped.

Returns:
    Number of frames successfully processed (``0`` on validation failure).

Examples:
    PyMOL> movie_transparency protein, 10, 50, 0.0, 1.0, 1
    PyMOL> movie_transparency ligand, 1, 100, 0.5, 0.0, 2, decrease

Since:
    1.0.0

See Also:
    fade_in, fade_out, transparency_pulse, transparency_range,
    set_frame_transparency
```

</details>

### `set_frame_transparency`

Set transparency for a single specific frame

- **Usage:** `set_frame_transparency [selection='all'] [frame=1] [transparency=0.5] [transparency_type=1]`
- **Since:** 1.0.0
- **Tags:** `animation`, `transparency`, `frame`, `movie`
- **See also:** `movie_transparency`, `transparency_sequence`, `transparency_range`

**Examples:**

```
set_frame_transparency protein, 50, 0.5, 1
set_frame_transparency complex, 100, 0.8, 0
```

<details><summary>Full docstring</summary>

```
Set transparency for a specific frame in a PyMOL movie.

Args:
    selection: PyMOL selection (default: ``"all"``).
    frame: Target frame number (default: ``1``).
    transparency: Transparency value 0.0–1.0 (default: ``0.5``).
    transparency_type: Transparency setting index 0–3 (default: ``1``).
        ``0`` = ``transparency`` (surface),
        ``1`` = ``cartoon_transparency``,
        ``2`` = ``sphere_transparency``,
        ``3`` = ``cgo_transparency``.

Returns:
    ``True`` on success, ``False`` on validation or command failure.

Examples:
    PyMOL> set_frame_transparency protein, 50, 0.5, 1
    PyMOL> set_frame_transparency complex, 100, 0.8, 0

Since:
    1.0.0

See Also:
    movie_transparency, transparency_sequence, transparency_range
```

</details>

### `suggest_transparency_type`

Suggest the best transparency type for a selection

- **Usage:** `suggest_transparency_type [selection='all']`
- **Since:** 1.0.0
- **Tags:** `animation`, `transparency`, `suggest`, `utility`
- **See also:** `movie_transparency`, `set_frame_transparency`

**Examples:**

```
suggest_transparency_type
suggest_transparency_type protein
suggest_transparency_type ligand_binding_site
```

<details><summary>Full docstring</summary>

```
Suggest the most appropriate transparency type for *selection*.

Inspects which PyMOL representations are active on the objects in
*selection* and returns the type integer that best matches them.

Args:
    selection: PyMOL selection to analyse (default: ``"all"``).

Returns:
    A ``(type_int, explanation)`` tuple where ``type_int`` is 0–3.

Examples:
    PyMOL> suggest_transparency_type
    PyMOL> suggest_transparency_type protein
    PyMOL> suggest_transparency_type ligand_binding_site

Since:
    1.0.0

See Also:
    movie_transparency, set_frame_transparency
```

</details>

### `transparency_pulse`

Create a pulsing transparency effect over multiple cycles

- **Usage:** `transparency_pulse [selection='all'] [start_frame=1] [end_frame=60] [min_transparency=0.0] [max_transparency=1.0] [transparency_type=0] [cycles=1]`
- **Since:** 1.0.0
- **Tags:** `animation`, `transparency`, `pulse`, `movie`
- **See also:** `fade_in`, `fade_out`, `movie_transparency`

**Examples:**

```
transparency_pulse protein, 1, 60
transparency_pulse ligand, 1, 90, 0.2, 0.8, 1, 3
```

<details><summary>Full docstring</summary>

```
Create a pulsing transparency effect over multiple cycles.

Divides the frame range into *cycles* equal segments, each containing
a fade-out followed by a fade-in.

Args:
    selection: PyMOL selection (default: ``"all"``).
    start_frame: First frame (default: ``1``).
    end_frame: Last frame (default: ``60``).
    min_transparency: Minimum transparency (default: ``0.0``).
    max_transparency: Maximum transparency (default: ``1.0``).
    transparency_type: Transparency setting index 0–3 (default: ``0``).
    cycles: Number of complete pulse cycles (default: ``1``).

Returns:
    Total number of frames successfully processed across all cycles.

Examples:
    PyMOL> transparency_pulse protein, 1, 60
    PyMOL> transparency_pulse ligand, 1, 90, 0.2, 0.8, 1, 3

Since:
    1.0.0

See Also:
    fade_in, fade_out, movie_transparency
```

</details>

### `transparency_range`

Set transparency across a frame range with a fixed step size

- **Usage:** `transparency_range [selection='all'] [start_frame=1] [end_frame=10] [start_transparency=0.0] [step=0.1] [direction='increase'] [transparency_type=1]`
- **Since:** 1.0.0
- **Tags:** `animation`, `transparency`, `range`, `step`, `movie`
- **See also:** `movie_transparency`, `set_frame_transparency`, `transparency_sequence`

**Examples:**

```
transparency_range protein, 385, 415, 0.1, 0.05, increase, 1
transparency_range ligand, 50, 60, 0.0, 0.2, increase, 2
```

<details><summary>Full docstring</summary>

```
Set transparency for a frame range using a fixed step increment.

Unlike :func:`movie_transparency` (which interpolates to a fixed end
value), this command advances by *step* per frame and clamps to [0, 1].

Args:
    selection: PyMOL selection (default: ``"all"``).
    start_frame: First frame (default: ``1``).
    end_frame: Last frame (default: ``10``).
    start_transparency: Initial transparency value 0.0–1.0 (default: ``0.0``).
    step: Transparency increment per frame (default: ``0.1``).
    direction: ``"increase"`` or ``"decrease"`` (default: ``"increase"``).
    transparency_type: Transparency setting index 0–3 (default: ``1``).

Returns:
    Number of frames successfully processed (``0`` on validation failure).

Examples:
    PyMOL> transparency_range protein, 385, 415, 0.1, 0.05, increase, 1
    PyMOL> transparency_range ligand, 50, 60, 0.0, 0.2, increase, 2

Since:
    1.0.0

See Also:
    movie_transparency, set_frame_transparency, transparency_sequence
```

</details>

### `transparency_sequence`

Set transparency for multiple frames via frame:value pairs

- **Usage:** `transparency_sequence [selection='all'] [frame_transparency_pairs=None] [transparency_type=1]`
- **Since:** 1.0.0
- **Tags:** `animation`, `transparency`, `sequence`, `movie`
- **See also:** `set_frame_transparency`, `movie_transparency`, `transparency_range`

**Examples:**

```
transparency_sequence protein, 100:0.0,110:0.5,120:1.0, 1
transparency_sequence chain A, 1:0.2,5:0.6,10:1.0, 0
```

<details><summary>Full docstring</summary>

```
Set transparency for multiple frames using ``frame:value`` pair strings.

Args:
    selection: PyMOL selection (default: ``"all"``).
    frame_transparency_pairs: Comma-separated ``frame:transparency`` pairs,
        e.g. ``"386:0.1,387:0.2,388:0.3"``.
    transparency_type: Transparency setting index 0–3 (default: ``1``).

Returns:
    Number of frames successfully processed (``0`` on parse or validation
    failure).

Examples:
    PyMOL> transparency_sequence protein, 100:0.0,110:0.5,120:1.0, 1
    PyMOL> transparency_sequence chain A, 1:0.2,5:0.6,10:1.0, 0

Since:
    1.0.0

See Also:
    set_frame_transparency, movie_transparency, transparency_range
```

</details>
