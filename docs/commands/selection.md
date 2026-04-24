# Selection

_1 command(s). Generated from the command registry — do not edit by hand._

## Commands in this category

- [`search_sequence`](#search_sequence) — Search for amino acid sequences in loaded structures using alignment

---

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
