# Selection

_3 command(s). Generated from the command registry — do not edit by hand._

## Commands in this category

- [`ions`](#ions) — Select common ions (NA, CL, MG, ...), or 'on'/'off' to show/hide them
- [`search_sequence`](#search_sequence) — Search for amino acid sequences in loaded structures using alignment
- [`water`](#water) — Select water (solvent), or 'on'/'off' to show/hide it

---

### `ions`

Select common ions (NA, CL, MG, ...), or 'on'/'off' to show/hide them

- **Usage:** `ions [mode='']`
- **Since:** 0.1.12
- **Tags:** `selection`, `solvent`, `ions`
- **See also:** `water`

**Examples:**

```
ions
ions on
ions off
```

<details><summary>Full docstring</summary>

```
Select common ions (NA, CL, MG, CA, ZN, ...), or show/hide them.

With no argument creates a selection named ``ions`` (or ``ions1``,
``ions2``, ... if the name is taken) matching popular ion residue names.

Args:
    mode: ``""`` to create a selection, ``"on"`` to show ions as lines,
        ``"off"`` to hide them.

Returns:
    Name of the created selection, or ``""`` for on/off modes.

Examples:
    PyMOL> ions
    PyMOL> ions on
    PyMOL> ions off

Since:
    0.1.12

See Also:
    water
```

</details>

### `search_sequence`

Search for amino acid sequences in loaded structures using alignment

- **Usage:** `search_sequence <sequence> [selection_name=''] [min_score=0.8]`
- **Since:** 1.0.0
- **Tags:** `sequence`, `alignment`, `search`, `biopython`
- **See also:** `pymolish_list`, `pymolish_search`

**Examples:**

```
search_sequence MVLSPADKTNVKAA
search_sequence ACDEFGH, mysel, 0.7
search_sequence PEPTIDE, hit, 0.9
```

<details><summary>Full docstring</summary>

```
Search for an amino acid sequence in all loaded structures.

Uses local pairwise alignment (Smith-Waterman via Biopython) to find
regions matching ``sequence`` in every loaded PyMOL object. Hits are
materialized as PyMOL selections named
``<selection_name>_<object>_<start>_<end>``.

Requires Biopython (``pip install pymolish[biopython]``).

Args:
    sequence: One-letter amino acid sequence to search for.
    selection_name: Base name for created selections. Defaults to
        ``seq_<first-5-chars>``.
    min_score: Minimum normalized alignment score in [0, 1].
        Defaults to ``0.8``.

Returns:
    List of selection names created (empty list on failure or no hits).

Examples:
    PyMOL> search_sequence MVLSPADKTNVKAA
    PyMOL> search_sequence ACDEFGH, mysel, 0.7
    PyMOL> search_sequence PEPTIDE, hit, 0.9

Since:
    1.0.0

See Also:
    pymolish_list, pymolish_search
```

</details>

### `water`

Select water (solvent), or 'on'/'off' to show/hide it

- **Usage:** `water [mode='']`
- **Since:** 0.1.12
- **Tags:** `selection`, `solvent`, `water`
- **See also:** `ions`

**Examples:**

```
water
water on
water off
```

<details><summary>Full docstring</summary>

```
Select water molecules, or show/hide them.

With no argument creates a selection named ``water`` (or ``water1``,
``water2``, ... if the name is taken) from ``solvent``.

Args:
    mode: ``""`` to create a selection, ``"on"`` to ``show lines, solvent``,
        ``"off"`` to ``hide everything, solvent``.

Returns:
    Name of the created selection, or ``""`` for on/off modes.

Examples:
    PyMOL> water
    PyMOL> water on
    PyMOL> water off

Since:
    0.1.12

See Also:
    ions
```

</details>
