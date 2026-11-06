# I/O

_9 command(s). Generated from the command registry — do not edit by hand._

## Commands in this category

- [`export_by_pattern`](#export_by_pattern) — Export objects whose names match a wildcard pattern
- [`export_byres_to_csv`](#export_byres_to_csv) — Write residues of a selection (chain, resname, resid) to CSV
- [`export_group`](#export_group) — Export all objects in a group as CIF/PDB/FASTA files
- [`export_objects`](#export_objects) — Export explicit PyMOL objects as CIF/PDB/FASTA files
- [`list_loadable_files`](#list_loadable_files) — Preview files that would be loaded without loading them
- [`load_files`](#load_files) — Load structure files from a directory with optional grouping
- [`load_recursive`](#load_recursive) — Recursively load structure files from a directory tree
- [`load_smiles`](#load_smiles) — Load SMILES or text/CSV files with conformers and grouping
- [`paste_smiles`](#paste_smiles) — Load the clipboard as a molecule if it is a SMILES (Ctrl+V)

---

### `export_by_pattern`

Export objects whose names match a wildcard pattern

- **Usage:** `export_by_pattern <pattern> [output_dir='.'] [format_type='cif'] [overwrite=False]`
- **Since:** 1.0.0
- **Tags:** `export`, `pattern`, `save`
- **See also:** `export_group`, `export_objects`

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

<details><summary>Full docstring</summary>

```
Write every residue in ``selection`` to ``outfile`` as CSV.

Output columns: ``chain,resname,resid``. Duplicates are dropped and the
rows are sorted deterministically.

Args:
    selection: PyMOL selection expression (e.g. ``"protein"``, ``"chain A"``).
    outfile: Destination CSV path. Parent directories are created if needed.

Returns:
    Number of unique residues written (``0`` on failure or empty selection).

Notes:
    Requires Python's standard-library ``csv`` module. If it is unavailable
    in PyMOL's runtime, reports an error without affecting other I/O commands.

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

### `load_smiles`

Load SMILES or text/CSV files with conformers and grouping

- **Usage:** `load_smiles <smiles> [name=None] [n_conformers=10] [mode='objects'] [seed=42] [group_name=None] [name_column=2]`
- **Since:** 0.1.24
- **Tags:** `smiles`, `rdkit`, `conformers`, `load`, `ligand`, `files`, `csv`, `group`
- **See also:** `paste_smiles`, `pymolish_install_deps`

<details><summary>Full docstring</summary>

```
Load molecules from inline SMILES or a text/CSV file with 3D conformers.

Conformers are generated with RDKit ETKDGv3, force-field minimized
(MMFF94, UFF fallback) and loaded without touching the disk.

Args:
    smiles: SMILES string or file path (quoted paths and ``~`` supported).
        Existing files and paths ending in ``.smi``, ``.smiles``, ``.txt``,
        or ``.csv`` are detected automatically. Text files use spaces/tabs;
        CSV uses commas or semicolons (auto-detected, quotes supported).
        Column 1 contains SMILES. Blank lines, ``#`` comments and an optional
        initial ``SMILES`` header are skipped; unused metadata is ignored.
        Files must be UTF-8 (an optional BOM is accepted).
    name: Fallback object name for one molecule, or naming prefix for multiple
        molecules. Defaults to an unused ``molNN`` name. File labels take
        precedence. Names are made legal in PyMOL and unique in the session.
    n_conformers: Maximum number of conformers (RMS pruning may yield fewer).
    mode: ``objects`` loads ``name_1 .. name_n`` grouped under ``name``;
        ``states`` loads all conformers as states of one object ``name``.
    seed: Random seed for reproducible embedding.
    group_name: Optional parent group for loaded molecules. Existing groups
        are reused; conformer groups remain nested beneath this group.
    name_column: One-based file column for object names/IDs (default: 2).
        Use ``0`` to ignore file names. Missing/empty names use ``name`` or
        an unused ``molNN`` name. Does not affect inline SMILES.

Returns:
    Names of successfully created objects. Invalid molecules are skipped;
    input errors or files with no molecules return an empty list.

Examples:
    PyMOL> load_smiles "CC(=O)Oc1ccccc1C(=O)O"
    PyMOL> load_smiles "CC(=O)Oc1ccccc1C(=O)O", aspirin, 5
    PyMOL> load_smiles "c1ccccc1O", phenol, 20, states
    PyMOL> load_smiles ligands.smi, lig, 3
    PyMOL> load_smiles ligands.csv, group_name=ligands, name_column=3
    PyMOL> load_smiles ligands.txt, name=lig, name_column=0

Since:
    0.1.24

See Also:
    paste_smiles, pymolish_install_deps
```

</details>

### `paste_smiles`

Load the clipboard as a molecule if it is a SMILES (Ctrl+V)

- **Usage:** `paste_smiles [n_conformers=10] [mode='objects']`
- **Since:** 0.1.24
- **Tags:** `smiles`, `rdkit`, `clipboard`, `paste`, `keybinding`
- **See also:** `load_smiles`, `pymolish_install_deps`

<details><summary>Full docstring</summary>

```
Load the clipboard as a molecule if it is a valid SMILES.

Bound to ``Ctrl+V`` while the 3D viewer has focus (the command line keeps
its normal paste behaviour). Non-SMILES text is ignored with a message.

Args:
    n_conformers: Maximum number of conformers to generate.
    mode: ``objects`` (default) or ``states``; see :func:`load_smiles`.

Returns:
    Names of the objects created (empty if nothing was loaded).

Examples:
    PyMOL> paste_smiles
    PyMOL> paste_smiles 3, states

Since:
    0.1.24

See Also:
    load_smiles, pymolish_install_deps
```

</details>
