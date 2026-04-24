# I/O

_7 command(s). Generated from the command registry — do not edit by hand._

## Commands in this category

- [`export_by_pattern`](#export_by_pattern) — Export objects whose names match a wildcard pattern
- [`export_byres_to_csv`](#export_byres_to_csv) — Write residues of a selection (chain, resname, resid) to CSV
- [`export_group`](#export_group) — Export all objects in a group as CIF/PDB/FASTA files
- [`export_objects`](#export_objects) — Export explicit PyMOL objects as CIF/PDB/FASTA files
- [`list_loadable_files`](#list_loadable_files) — Preview files that would be loaded without loading them
- [`load_files`](#load_files) — Load structure files from a directory with optional grouping
- [`load_recursive`](#load_recursive) — Recursively load structure files from a directory tree

---

### `export_by_pattern`

Export objects whose names match a wildcard pattern

- **Usage:** `export_by_pattern <pattern> [output_dir='.'] [format_type='cif'] [overwrite=False]`
- **Since:** 1.0.0
- **Tags:** `export`, `pattern`, `save`
- **See also:** `export_group`, `export_objects`

**Examples:**

```
export_by_pattern protein_*
export_by_pattern chain_*, ./out, pdb
```

<details><summary>Full docstring</summary>

```
Export all objects whose names match ``pattern``.

Args:
    pattern: Wildcard pattern (``*`` and ``?`` supported).
    output_dir: Destination directory (created if missing).
    format_type: ``"cif"``, ``"pdb"``, or ``"fasta"``.
    overwrite: When truthy, overwrite existing files.

Returns:
    List of paths written (strings).

Examples:
    PyMOL> export_by_pattern protein_*
    PyMOL> export_by_pattern chain_*, ./out, pdb

Since:
    1.0.0

See Also:
    export_group, export_objects
```

</details>

### `export_byres_to_csv`

Write residues of a selection (chain, resname, resid) to CSV

- **Usage:** `export_byres_to_csv <selection> <outfile>`
- **Since:** 1.0.0
- **Tags:** `export`, `residues`, `csv`
- **See also:** `export_group`

**Examples:**

```
export_byres_to_csv protein, residues.csv
export_byres_to_csv chain A, chain_a.csv
export_byres_to_csv resi 1-50, residues_1_50.csv
```

<details><summary>Full docstring</summary>

```
Write every residue in ``selection`` to ``outfile`` as CSV.

Output columns: ``chain,resname,resid``. Duplicates are dropped and the
rows are sorted deterministically.

Args:
    selection: PyMOL selection expression (e.g. ``"protein"``, ``"chain A"``).
    outfile: Destination CSV path. Parent directories are created if needed.

Returns:
    Number of unique residues written (``0`` on empty or failed selection).

Examples:
    PyMOL> export_byres_to_csv protein, residues.csv
    PyMOL> export_byres_to_csv chain A, ./out/chain_a.csv
    PyMOL> export_byres_to_csv resi 1-50, residues_1_50.csv

Since:
    1.0.0

See Also:
    export_group, export_objects
```

</details>

### `export_group`

Export all objects in a group as CIF/PDB/FASTA files

- **Usage:** `export_group <group_name> [output_dir='.'] [format_type='cif'] [overwrite=False]`
- **Since:** 1.0.0
- **Tags:** `export`, `group`, `save`
- **See also:** `export_objects`, `export_by_pattern`, `export_byres_to_csv`

**Examples:**

```
export_group my_structures
export_group proteins, ., pdb
export_group sequences, ., fasta
export_group models, ./out, cif, 1
```

<details><summary>Full docstring</summary>

```
Export all objects in a PyMOL group to individual structure files.

Args:
    group_name: Name of the PyMOL group to export.
    output_dir: Destination directory (created if missing).
    format_type: Output format — ``"cif"``, ``"pdb"``, or ``"fasta"``.
    overwrite: When truthy, overwrite existing files at the destination.

Returns:
    List of paths written (strings).

Examples:
    PyMOL> export_group my_structures
    PyMOL> export_group proteins, ., pdb
    PyMOL> export_group sequences, ., fasta
    PyMOL> export_group models, ./exports, cif, 1

Since:
    1.0.0

See Also:
    export_objects, export_by_pattern
```

</details>

### `export_objects`

Export explicit PyMOL objects as CIF/PDB/FASTA files

- **Usage:** `export_objects <object_names> [output_dir='.'] [format_type='cif'] [overwrite=False]`
- **Since:** 1.0.0
- **Tags:** `export`, `objects`, `save`
- **See also:** `export_group`, `export_by_pattern`

**Examples:**

```
export_objects obj1,obj2,obj3
export_objects obj1,obj2, ./out, pdb
```

<details><summary>Full docstring</summary>

```
Export explicit PyMOL objects to structure files.

Args:
    object_names: Comma-separated string or list of object names.
    output_dir: Destination directory (created if missing).
    format_type: ``"cif"``, ``"pdb"``, or ``"fasta"``.
    overwrite: When truthy, overwrite existing files.

Returns:
    List of paths written (strings).

Examples:
    PyMOL> export_objects obj1,obj2,obj3
    PyMOL> export_objects obj1,obj2, ./out, pdb

Since:
    1.0.0

See Also:
    export_group, export_by_pattern
```

</details>

### `list_loadable_files`

Preview files that would be loaded without loading them

- **Usage:** `list_loadable_files [dir_name='.'] [suffix='pdb'] [recursive=False] [name_filter=None] [exclude_subdirs=None] [max_depth=3]`
- **Since:** 1.0.0
- **Tags:** `preview`, `list`, `directory`
- **See also:** `load_files`, `load_recursive`

**Examples:**

```
list_loadable_files
list_loadable_files /tmp, sdf, 1
list_loadable_files ., cif, 0, model_*
list_loadable_files ., pdb, 1, , traj
```

<details><summary>Full docstring</summary>

```
Preview files that would be loaded without actually loading them.

Args:
    dir_name: Directory path to search.
    suffix: File extension without leading dot.
    recursive: When truthy, walk subdirectories up to ``max_depth``.
    name_filter: Basename wildcard filter.
    exclude_subdirs: Directory names to skip during recursive walks.
    max_depth: Maximum recursion depth (default: 3).

Returns:
    List of file paths that would be loaded (strings, sorted).

Examples:
    PyMOL> list_loadable_files
    PyMOL> list_loadable_files /tmp, sdf, 1
    PyMOL> list_loadable_files ., pdb, 1, , traj

Since:
    1.0.0

See Also:
    load_files, load_recursive
```

</details>

### `load_files`

Load structure files from a directory with optional grouping

- **Usage:** `load_files [dir_name='.'] [suffix='pdb'] [group_name=None] [prefix=''] [name_filter=None] [recursive=False] [exclude_subdirs=None] [max_depth=3] [verbose=True]`
- **Since:** 1.0.0
- **Tags:** `batch`, `load`, `directory`, `files`
- **See also:** `load_recursive`, `list_loadable_files`, `export_group`

**Examples:**

```
load_files
load_files /tmp, sdf
load_files ., pdb, my_proteins
load_files ., pdb, proteins, loaded_
load_files ., cif, , , model_*
load_files ., pdb, , , , 1, traj
```

<details><summary>Full docstring</summary>

```
Load multiple structure files from a directory into PyMOL.

Scans ``dir_name`` for files with the given ``suffix``, loads each as a
PyMOL object, resolves naming conflicts with a numeric suffix, and
optionally groups the loaded objects.

Args:
    dir_name: Directory path to load from (default: current directory).
    suffix: File extension without leading dot (e.g. ``"pdb"``, ``"cif"``).
    group_name: Optional group for loaded objects.
    prefix: String prepended to each object name.
    name_filter: Wildcard pattern applied to basenames (e.g. ``"model_*"``).
    recursive: When truthy, walk subdirectories up to ``max_depth``.
    exclude_subdirs: Directory names to skip during recursive walks.
    max_depth: Maximum recursion depth (default: 3).
    verbose: When truthy, print per-file progress.

Returns:
    List of successfully loaded object names.

Examples:
    PyMOL> load_files
    PyMOL> load_files /tmp, sdf
    PyMOL> load_files ., pdb, my_proteins
    PyMOL> load_files ., pdb, , , , 1, "traj, cache"

Since:
    1.0.0

See Also:
    load_recursive, list_loadable_files, export_group
```

</details>

### `load_recursive`

Recursively load structure files from a directory tree

- **Usage:** `load_recursive [dir_name='.'] [suffix='pdb'] [group_name=None] [prefix=''] [name_filter=None] [max_depth=3] [verbose=True]`
- **Since:** 1.0.0
- **Tags:** `batch`, `load`, `recursive`
- **See also:** `load_files`, `list_loadable_files`

**Examples:**

```
load_recursive
load_recursive /data, sdf, ligands
load_recursive ., cif, , , model_*
load_recursive ., pdb, , , , 2
```

<details><summary>Full docstring</summary>

```
Recursively load files from ``dir_name`` and subdirectories.

Convenience wrapper around :func:`load_files` with ``recursive=True``.

Args:
    dir_name: Root directory to walk.
    suffix: File extension without leading dot.
    group_name: Optional group for loaded objects.
    prefix: Object-name prefix.
    name_filter: Basename wildcard filter.
    max_depth: Maximum recursion depth (default: 3).
    verbose: When truthy, print per-file progress.

Returns:
    List of successfully loaded object names.

Examples:
    PyMOL> load_recursive
    PyMOL> load_recursive /data, sdf, ligands
    PyMOL> load_recursive ., cif, , , model_*

Since:
    1.0.0

See Also:
    load_files, list_loadable_files
```

</details>
