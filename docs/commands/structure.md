# Structure

_8 command(s). Generated from the command registry — do not edit by hand._

## Commands in this category

- [`cluster_ligands_by_position`](#cluster_ligands_by_position) — Cluster ligands by 3-D centroid into new PyMOL groups (requires numpy)
- [`cluster_ligands_from_group`](#cluster_ligands_from_group) — Cluster ligands from a named PyMOL group (requires numpy)
- [`fetch_by_uniprot`](#fetch_by_uniprot) — Fetch PDB structures for a UniProt accession via RCSB/UniProt APIs (requires requests)
- [`list_objects_with_prefix`](#list_objects_with_prefix) — List PyMOL objects whose names start with a given prefix
- [`list_uniprot_structures`](#list_uniprot_structures) — List PDB structures for a UniProt accession without loading them (requires requests)
- [`multialign`](#multialign) — Align multiple structures to a reference and report RMSD statistics
- [`remove_ions`](#remove_ions) — Remove common small ions from a PyMOL selection
- [`remove_metals`](#remove_metals) — Remove common metal atoms from a PyMOL selection

---

### `cluster_ligands_by_position`

Cluster ligands by 3-D centroid into new PyMOL groups (requires numpy)

- **Usage:** `cluster_ligands_by_position <ligand_group_or_selection> [num_groups=2] [cluster_method='kmeans'] [distance_cutoff=10.0] [group_prefix='ligand_cluster'] [verbose=True]`
- **Since:** 1.0.0
- **Tags:** `clustering`, `ligands`, `spatial`, `numpy`, `groups`
- **See also:** `cluster_ligands_from_group`

**Examples:**

```
cluster_ligands_by_position ligands, 3
cluster_ligands_by_position hetero, 4, hierarchical, 15.0
cluster_ligands_by_position drug_group, 2, distance, 10.0, my_clusters
```

<details><summary>Full docstring</summary>

```
Cluster ligands by 3-D centroid into new PyMOL groups.

Resolves *ligand_group_or_selection* to individual objects, computes each
object's centroid, then clusters using K-means, single-linkage hierarchical,
or distance-cutoff partitioning.  Each cluster is stored as a new PyMOL
group named ``{group_prefix}_{n}``.

Requires **numpy** — install via ``pip install pymolish[numpy]``.

Args:
    ligand_group_or_selection: PyMOL group or selection containing ligands.
    num_groups: Number of clusters (ignored for ``"distance"`` method).
    cluster_method: ``"kmeans"`` (default), ``"hierarchical"``, or
        ``"distance"``.
    distance_cutoff: Max inter-centroid distance (Å) for the ``"distance"``
        method.
    group_prefix: Prefix for created group names.
    verbose: When truthy, log per-object centroids and cluster assignments.

Returns:
    Dict mapping each created group name to the list of member object names.
    Returns ``{}`` on error (missing dep, too few ligands, unknown method).

Examples:
    PyMOL> cluster_ligands_by_position ligands, 3
    PyMOL> cluster_ligands_by_position hetero, 4, hierarchical, 15.0
    PyMOL> cluster_ligands_by_position drug_group, 2, distance, 10.0, my_cl

Since:
    1.0.0

See Also:
    cluster_ligands_from_group
```

</details>

### `cluster_ligands_from_group`

Cluster ligands from a named PyMOL group (requires numpy)

- **Usage:** `cluster_ligands_from_group <group_name> [num_groups=2] [cluster_method='kmeans'] [distance_cutoff=10.0] [group_prefix='ligand_cluster']`
- **Since:** 1.0.0
- **Tags:** `clustering`, `ligands`, `groups`, `numpy`
- **See also:** `cluster_ligands_by_position`

**Examples:**

```
cluster_ligands_from_group my_ligands, 2
cluster_ligands_from_group compounds, 5, hierarchical
cluster_ligands_from_group drug_group, 3, distance, 12.0
```

<details><summary>Full docstring</summary>

```
Convenience wrapper: cluster ligands from a named PyMOL group.

Delegates to :func:`cluster_ligands_by_position` with ``verbose=True``.

Requires **numpy** — install via ``pip install pymolish[numpy]``.

Args:
    group_name: Name of PyMOL group containing ligand objects.
    num_groups: Number of clusters to create.
    cluster_method: ``"kmeans"``, ``"hierarchical"``, or ``"distance"``.
    distance_cutoff: Distance cutoff (Å) for the ``"distance"`` method.
    group_prefix: Prefix for new group names.

Returns:
    Same dict as :func:`cluster_ligands_by_position`.

Examples:
    PyMOL> cluster_ligands_from_group my_ligands, 2
    PyMOL> cluster_ligands_from_group compounds, 5, hierarchical
    PyMOL> cluster_ligands_from_group drug_group, 3, distance, 12.0

Since:
    1.0.0

See Also:
    cluster_ligands_by_position
```

</details>

### `fetch_by_uniprot`

Fetch PDB structures for a UniProt accession via RCSB/UniProt APIs (requires requests)

- **Usage:** `fetch_by_uniprot <uniprot_id> [max_structures=10] [verbose=True]`
- **Since:** 1.0.0
- **Tags:** `fetch`, `uniprot`, `pdb`, `network`
- **See also:** `list_uniprot_structures`

**Examples:**

```
fetch_by_uniprot P04637
fetch_by_uniprot P38398, 5
fetch_by_uniprot Q9Y6R4, 3, 0
```

<details><summary>Full docstring</summary>

```
Fetch PDB structures for a UniProt accession into PyMOL.

Tries three search strategies in order (RCSB GraphQL → UniProt REST →
Biopython) and loads up to *max_structures* PDB entries via
:pymol:`fetch`.

Requires **requests** (and optionally **biopython**) — install with
``pip install pymolish[biopython]``.

Args:
    uniprot_id: UniProt accession ID (e.g. ``"P04637"``).
    max_structures: Maximum number of PDB entries to load.
    verbose: When truthy, log per-structure progress.

Returns:
    List of successfully loaded PDB IDs (uppercase, e.g. ``["1TUP"]``).

Examples:
    PyMOL> fetch_by_uniprot P04637
    PyMOL> fetch_by_uniprot P38398, 5
    PyMOL> fetch_by_uniprot Q9Y6R4, 3, 0

Since:
    1.0.0

See Also:
    list_uniprot_structures
```

</details>

### `list_objects_with_prefix`

List PyMOL objects whose names start with a given prefix

- **Usage:** `list_objects_with_prefix [prefix='']`
- **Since:** 1.0.0
- **Tags:** `list`, `objects`, `prefix`, `utility`
- **See also:** `multialign`

**Examples:**

```
list_objects_with_prefix protein_
list_objects_with_prefix chain_A
list_objects_with_prefix
```

<details><summary>Full docstring</summary>

```
List all PyMOL objects whose names start with *prefix*.

Args:
    prefix: Name prefix to filter by. When empty, all objects are returned.

Returns:
    Matching object names (sorted).

Examples:
    PyMOL> list_objects_with_prefix protein_
    PyMOL> list_objects_with_prefix chain_A
    PyMOL> list_objects_with_prefix

Since:
    1.0.0

See Also:
    multialign
```

</details>

### `list_uniprot_structures`

List PDB structures for a UniProt accession without loading them (requires requests)

- **Usage:** `list_uniprot_structures <uniprot_id> [show_details=True]`
- **Since:** 1.0.0
- **Tags:** `list`, `uniprot`, `pdb`, `network`
- **See also:** `fetch_by_uniprot`

**Examples:**

```
list_uniprot_structures P04637
list_uniprot_structures P38398, 1
list_uniprot_structures Q9Y6R4, 0
```

<details><summary>Full docstring</summary>

```
List PDB structures for a UniProt accession without loading them.

Queries the same search backends as :func:`fetch_by_uniprot` and prints
the found PDB IDs with optional per-entry metadata from the RCSB REST API.

Requires **requests** (and optionally **biopython**) — install with
``pip install pymolish[biopython]``.

Args:
    uniprot_id: UniProt accession ID (e.g. ``"P04637"``).
    show_details: When truthy, fetch RCSB metadata for each entry (title,
        resolution, method).

Returns:
    List of found PDB IDs (may be empty).

Examples:
    PyMOL> list_uniprot_structures P04637
    PyMOL> list_uniprot_structures P38398, 1
    PyMOL> list_uniprot_structures Q9Y6R4, 0

Since:
    1.0.0

See Also:
    fetch_by_uniprot
```

</details>

### `multialign`

Align multiple structures to a reference and report RMSD statistics

- **Usage:** `multialign <group_or_selection> <target> [verbose=True]`
- **Since:** 1.0.0
- **Tags:** `alignment`, `rmsd`, `structure`, `multi`
- **See also:** `list_objects_with_prefix`

**Examples:**

```
multialign my_structures, reference_protein
multialign protein_*, template_1
multialign Estrogen, 1A52
multialign Estrogen, 1A52, 0
```

<details><summary>Full docstring</summary>

```
Align multiple structures to a reference and report RMSD statistics.

Resolves *group_or_selection* to a list of PyMOL objects (group members,
selection intersection, or wildcard pattern), aligns each to *target* via
:pymol:`align`, and prints a summary with min/max/mean/median RMSD.

Args:
    group_or_selection: Group name, selection, or glob pattern containing
        the structures to align.
    target: PyMOL object name used as the alignment reference.
    verbose: When truthy, print per-structure progress and the final
        statistics table.

Returns:
    Mapping of ``{object_name: rmsd}`` for every successful alignment.
    Failed structures are omitted.

Examples:
    PyMOL> multialign my_structures, reference_protein
    PyMOL> multialign protein_*, template_1
    PyMOL> multialign Estrogen, 1A52, 0

Since:
    1.0.0

See Also:
    list_objects_with_prefix
```

</details>

### `remove_ions`

Remove common small ions from a PyMOL selection

- **Usage:** `remove_ions [selection='all']`
- **Since:** 1.0.0
- **Tags:** `cleanup`, `ions`, `remove`, `structure`
- **See also:** `remove_metals`

**Examples:**

```
remove_ions
remove_ions protein_complex
remove_ions chain A
```

<details><summary>Full docstring</summary>

```
Remove common small ions from *selection*.

Deletes atoms matching any of the curated ion residue names within the
given PyMOL selection: ``NA``, ``K``, ``CL``, ``CA``, ``MG``, ``ZN``,
``MN``, ``FE``, ``CU``, ``CD``, ``SO4``, ``PO4``.

Args:
    selection: PyMOL selection expression (default: ``"all"``).

Returns:
    Number of residue names removed (i.e. iterations that found matches,
    not total atoms).

Examples:
    PyMOL> remove_ions
    PyMOL> remove_ions protein_complex
    PyMOL> remove_ions chain A

Since:
    1.0.0

See Also:
    remove_metals
```

</details>

### `remove_metals`

Remove common metal atoms from a PyMOL selection

- **Usage:** `remove_metals [selection='all']`
- **Since:** 1.0.0
- **Tags:** `cleanup`, `metals`, `remove`, `structure`
- **See also:** `remove_ions`

**Examples:**

```
remove_metals
remove_metals my_protein
remove_metals chain B
```

<details><summary>Full docstring</summary>

```
Remove common metal atoms from *selection*.

Deletes atoms matching any of the curated metal residue names within the
given PyMOL selection: ``ZN``, ``FE``, ``CU``, ``MN``, ``MG``, ``CD``,
``CO``, ``NI``, ``SR``, ``BA``, ``CS``, ``PB``, ``HG``, ``AU``, ``PT``,
``LI``, ``AL``, ``GA``, ``IN``, ``IR``, ``OS``, ``RH``, ``RU``.

Args:
    selection: PyMOL selection expression (default: ``"all"``).

Returns:
    Number of residue names removed (i.e. iterations that found matches,
    not total atoms).

Examples:
    PyMOL> remove_metals
    PyMOL> remove_metals my_protein
    PyMOL> remove_metals chain B

Since:
    1.0.0

See Also:
    remove_ions
```

</details>
