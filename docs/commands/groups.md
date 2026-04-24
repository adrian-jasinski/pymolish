# Groups

_18 command(s). Generated from the command registry — do not edit by hand._

## Commands in this category

- [`copy_group`](#copy_group) — Copy a group with renamed member objects
- [`copy_group_objects`](#copy_group_objects) — Copy explicitly listed objects into a new group with renamed members
- [`create_sorted_group`](#create_sorted_group) — Create a new group whose members are sorted alphabetically
- [`extract_chain_from_group`](#extract_chain_from_group) — Extract a single chain from every object in a group or pattern
- [`extract_chains_from_group`](#extract_chains_from_group) — Extract multiple chains from every object in a group or pattern
- [`group_disable`](#group_disable) — Disable objects in a group or matching a pattern
- [`group_enable`](#group_enable) — Enable objects in a group or matching a pattern
- [`group_info`](#group_info) — Display metadata and sorting status for a group
- [`group_next`](#group_next) — Show the next object in a group (one at a time)
- [`group_previous`](#group_previous) — Show the previous object in a group (one at a time)
- [`group_status`](#group_status) — Report enabled/disabled state of objects in a group or pattern
- [`group_toggle`](#group_toggle) — Toggle visibility of objects in a group or matching a pattern
- [`list_group_copies`](#list_group_copies) — Find all copies of objects belonging to a group
- [`list_merged_objects`](#list_merged_objects) — List all objects that contain a merged structure
- [`merge_to_group`](#merge_to_group) — Merge a structure into every object in a group
- [`merge_to_objects`](#merge_to_objects) — Merge a structure into specific objects
- [`sort_all_groups`](#sort_all_groups) — Sort objects in every PyMOL group alphabetically
- [`sort_group_objects`](#sort_group_objects) — Sort all objects within a group alphabetically

---

### `copy_group`

Copy a group with renamed member objects

- **Usage:** `copy_group <group_name> [new_group_name=''] [object_suffix='_cpy']`
- **Since:** 1.0.0
- **Tags:** `group`, `copy`, `duplicate`
- **See also:** `copy_group_objects`, `list_group_copies`

**Examples:**

```
copy_group my_structures
copy_group proteins, proteins_backup
copy_group data, data_copy, _backup
```

<details><summary>Full docstring</summary>

```
Copy a group, renaming each member object with *object_suffix*.

Args:
    group_name: Name of the source group.
    new_group_name: Name for the new group.  Defaults to
        ``<group_name>_cpy``.
    object_suffix: Suffix appended to each copied object name (default
        ``"_cpy"``).

Returns:
    List of successfully copied object names in the new group.

Examples:
    PyMOL> copy_group my_structures
    PyMOL> copy_group proteins, proteins_backup
    PyMOL> copy_group data, data_copy, _backup

Since:
    1.0.0

See Also:
    copy_group_objects, list_group_copies
```

</details>

### `copy_group_objects`

Copy explicitly listed objects into a new group with renamed members

- **Usage:** `copy_group_objects <object_names> <new_group_name> [object_suffix='_cpy']`
- **Since:** 1.0.0
- **Tags:** `group`, `copy`, `objects`
- **See also:** `copy_group`, `list_group_copies`

**Examples:**

```
copy_group_objects obj1,obj2,obj3, my_backup
copy_group_objects protein1,protein2, backup_group, _backup
```

<details><summary>Full docstring</summary>

```
Copy explicitly listed objects into a new group with renamed members.

Args:
    object_names: Comma-separated object names.
    new_group_name: Name of the destination group (created if absent).
    object_suffix: Suffix appended to each copied object name (default
        ``"_cpy"``).

Returns:
    List of successfully copied object names.

Examples:
    PyMOL> copy_group_objects obj1,obj2,obj3, my_backup
    PyMOL> copy_group_objects protein1,protein2, backup_group, _backup

Since:
    1.0.0

See Also:
    copy_group, list_group_copies
```

</details>

### `create_sorted_group`

Create a new group whose members are sorted alphabetically

- **Usage:** `create_sorted_group <source_group> [new_group_name='']`
- **Since:** 1.0.0
- **Tags:** `group`, `sort`, `create`
- **See also:** `sort_group_objects`, `group_info`

**Examples:**

```
create_sorted_group my_group
create_sorted_group proteins, proteins_sorted
```

<details><summary>Full docstring</summary>

```
Create a new group whose members are the sorted objects from *source_group*.

The source group is left untouched.

Args:
    source_group: Name of an existing group to copy from.
    new_group_name: Name for the new sorted group.  Defaults to
        ``<source_group>_sorted``.

Returns:
    Sorted list of object names added to the new group, or an empty list
    on failure.

Examples:
    PyMOL> create_sorted_group my_group
    PyMOL> create_sorted_group proteins, proteins_sorted

Since:
    1.0.0

See Also:
    sort_group_objects, group_info
```

</details>

### `extract_chain_from_group`

Extract a single chain from every object in a group or pattern

- **Usage:** `extract_chain_from_group <group_pattern> <chain> [prefix='chain_extract'] [add_to_group=True]`
- **Since:** 1.0.0
- **Tags:** `group`, `chain`, `extract`
- **See also:** `extract_chains_from_group`

**Examples:**

```
extract_chain_from_group my_group, A
extract_chain_from_group protein_*, B, my_prefix
extract_chain_from_group complex, C, chains, 0
```

<details><summary>Full docstring</summary>

```
Extract a single chain from every object matching *group_pattern*.

For each resolved target object creates a new object named
``<prefix>_<source>_<chain>`` containing only the specified chain.  If an
object with that name already exists it is replaced.

Args:
    group_pattern: Group name, object name, or wildcard pattern.
    chain: Chain identifier to extract (e.g. ``"A"``).
    prefix: Prefix for newly created object names (default
        ``"chain_extract"``).
    add_to_group: When truthy, collect extracted objects into a group
        named ``<group_pattern>_chain_<chain>`` (default ``True``).

Returns:
    List of created object names.

Examples:
    PyMOL> extract_chain_from_group my_group, A
    PyMOL> extract_chain_from_group protein_*, B, my_prefix
    PyMOL> extract_chain_from_group complex, C, chains, 0

Since:
    1.0.0

See Also:
    extract_chains_from_group
```

</details>

### `extract_chains_from_group`

Extract multiple chains from every object in a group or pattern

- **Usage:** `extract_chains_from_group <group_pattern> <chains> [prefix='chain_extract'] [add_to_group=True]`
- **Since:** 1.0.0
- **Tags:** `group`, `chain`, `extract`, `batch`
- **See also:** `extract_chain_from_group`

**Examples:**

```
extract_chains_from_group my_group, A,B
extract_chains_from_group proteins, A,B,C
extract_chains_from_group complex, A,B, my_prefix, 0
```

<details><summary>Full docstring</summary>

```
Extract multiple chains from every object matching *group_pattern*.

Delegates each chain to :func:`extract_chain_from_group`.

Args:
    group_pattern: Group name, object name, or wildcard pattern.
    chains: Comma-separated chain identifiers (e.g. ``"A,B,C"``).
    prefix: Prefix for newly created object names.
    add_to_group: When truthy, collect each chain's objects into its own
        group (default ``True``).

Returns:
    Dict mapping each chain identifier to the list of created objects.

Examples:
    PyMOL> extract_chains_from_group my_group, A,B
    PyMOL> extract_chains_from_group proteins, A,B,C
    PyMOL> extract_chains_from_group complex, A,B, my_prefix, 0

Since:
    1.0.0

See Also:
    extract_chain_from_group
```

</details>

### `group_disable`

Disable objects in a group or matching a pattern

- **Usage:** `group_disable <group_pattern> [each=1]`
- **Since:** 1.0.0
- **Tags:** `group`, `disable`, `visibility`
- **See also:** `group_enable`, `group_toggle`, `group_status`

**Examples:**

```
group_disable my_group
group_disable my_group, 2
group_disable chain_*
```

<details><summary>Full docstring</summary>

```
Disable objects resolved from *group_pattern*.

Args:
    group_pattern: Group name, object name, or wildcard pattern.
    each: Disable every *nth* object (``1`` = all, ``2`` = every second, …).

Returns:
    Names of objects that were successfully disabled.

Examples:
    PyMOL> group_disable my_group
    PyMOL> group_disable my_group, 2
    PyMOL> group_disable chain_*

Since:
    1.0.0

See Also:
    group_enable, group_toggle, group_status
```

</details>

### `group_enable`

Enable objects in a group or matching a pattern

- **Usage:** `group_enable <group_pattern> [each=1]`
- **Since:** 1.0.0
- **Tags:** `group`, `enable`, `visibility`
- **See also:** `group_disable`, `group_toggle`, `group_status`

**Examples:**

```
group_enable my_group
group_enable my_group, 2
group_enable chain_*
```

<details><summary>Full docstring</summary>

```
Enable objects resolved from *group_pattern*.

Args:
    group_pattern: Group name, object name, or wildcard pattern.
    each: Enable every *nth* object (``1`` = all, ``2`` = every second, …).

Returns:
    Names of objects that were successfully enabled.

Examples:
    PyMOL> group_enable my_group
    PyMOL> group_enable my_group, 2
    PyMOL> group_enable chain_*

Since:
    1.0.0

See Also:
    group_disable, group_toggle, group_status
```

</details>

### `group_info`

Display metadata and sorting status for a group

- **Usage:** `group_info <group_name>`
- **Since:** 1.0.0
- **Tags:** `group`, `info`, `inspect`
- **See also:** `sort_group_objects`, `create_sorted_group`

**Examples:**

```
group_info my_proteins
group_info structures_group
```

<details><summary>Full docstring</summary>

```
Return metadata about a PyMOL group.

Args:
    group_name: Name of an existing PyMOL group.

Returns:
    Dict with keys ``"name"``, ``"object_count"``, ``"objects"``, and
    ``"is_sorted"``.  An empty dict is returned when the group is not found.

Examples:
    PyMOL> group_info my_proteins
    PyMOL> group_info structures_group

Since:
    1.0.0

See Also:
    sort_group_objects, create_sorted_group
```

</details>

### `group_next`

Show the next object in a group (one at a time)

- **Usage:** `group_next [group_name='']`
- **Since:** 1.0.0
- **Tags:** `group`, `navigate`, `next`
- **See also:** `group_previous`, `group_enable`, `group_disable`

**Examples:**

```
group_next
group_next my_group
```

<details><summary>Full docstring</summary>

```
Show the next object in a group (one at a time).

Disables the current object and enables the next one (wrapping around).
When no object is enabled, enables the first.  When more than one object
is enabled, asks the user to run ``group_disable`` first.

Args:
    group_name: Group to navigate.  When omitted, the function infers
        the active group from the scene (works best with a single group).

Returns:
    Name of the newly shown object, or ``None`` if navigation was not
    possible.

Examples:
    PyMOL> group_next
    PyMOL> group_next my_group

Since:
    1.0.0

See Also:
    group_previous, group_enable, group_disable
```

</details>

### `group_previous`

Show the previous object in a group (one at a time)

- **Usage:** `group_previous [group_name='']`
- **Since:** 1.0.0
- **Tags:** `group`, `navigate`, `previous`
- **See also:** `group_next`, `group_enable`, `group_disable`

**Examples:**

```
group_previous
group_previous my_group
```

<details><summary>Full docstring</summary>

```
Show the previous object in a group (one at a time).

Same resolution rules as :func:`group_next` but moves in the reverse
direction.  When no object is enabled, enables the last.

Args:
    group_name: Group to navigate.  When omitted, the active group is
        inferred from the scene.

Returns:
    Name of the newly shown object, or ``None`` if navigation was not
    possible.

Examples:
    PyMOL> group_previous
    PyMOL> group_previous my_group

Since:
    1.0.0

See Also:
    group_next, group_enable, group_disable
```

</details>

### `group_status`

Report enabled/disabled state of objects in a group or pattern

- **Usage:** `group_status <group_pattern>`
- **Since:** 1.0.0
- **Tags:** `group`, `status`, `visibility`
- **See also:** `group_enable`, `group_disable`, `group_toggle`

**Examples:**

```
group_status my_group
group_status chain_*
```

<details><summary>Full docstring</summary>

```
Report the enabled/disabled state of objects matching *group_pattern*.

Args:
    group_pattern: Group name, object name, or wildcard pattern.

Returns:
    Dict with keys ``"enabled"`` and ``"disabled"`` listing matched objects
    in each state.  Both lists are empty when nothing matches.

Examples:
    PyMOL> group_status my_group
    PyMOL> group_status chain_*

Since:
    1.0.0

See Also:
    group_enable, group_disable, group_toggle
```

</details>

### `group_toggle`

Toggle visibility of objects in a group or matching a pattern

- **Usage:** `group_toggle <group_pattern> [each=1]`
- **Since:** 1.0.0
- **Tags:** `group`, `toggle`, `visibility`
- **See also:** `group_enable`, `group_disable`, `group_status`

**Examples:**

```
group_toggle my_group
group_toggle my_group, 2
```

<details><summary>Full docstring</summary>

```
Toggle visibility of objects resolved from *group_pattern*.

Objects that are currently enabled are disabled and vice versa.

Args:
    group_pattern: Group name, object name, or wildcard pattern.
    each: Toggle every *nth* object (``1`` = all, ``2`` = every second, …).

Returns:
    Dict with keys ``"enabled"`` and ``"disabled"`` listing the objects
    that were transitioned into each state.

Examples:
    PyMOL> group_toggle my_group
    PyMOL> group_toggle my_group, 2

Since:
    1.0.0

See Also:
    group_enable, group_disable, group_status
```

</details>

### `list_group_copies`

Find all copies of objects belonging to a group

- **Usage:** `list_group_copies <group_name>`
- **Since:** 1.0.0
- **Tags:** `group`, `copy`, `list`
- **See also:** `copy_group`, `copy_group_objects`

**Examples:**

```
list_group_copies my_structures
```

<details><summary>Full docstring</summary>

```
Find objects whose names start with any member of *group_name*.

This heuristic detects copies created by :func:`copy_group`.

Args:
    group_name: Name of the original source group.

Returns:
    Dict mapping each original member name to the list of copies found.
    Only members that have at least one copy are included.

Examples:
    PyMOL> list_group_copies my_structures

Since:
    1.0.0

See Also:
    copy_group, copy_group_objects
```

</details>

### `list_merged_objects`

List all objects that contain a merged structure

- **Usage:** `list_merged_objects <struct_name>`
- **Since:** 1.0.0
- **Tags:** `group`, `merge`, `list`
- **See also:** `merge_to_group`, `merge_to_objects`

**Examples:**

```
list_merged_objects ligand1
```

<details><summary>Full docstring</summary>

```
Find all objects whose names contain ``_with_<struct_name>``.

Args:
    struct_name: Structure name to search for in object names.

Returns:
    Sorted list of matching object names.

Examples:
    PyMOL> list_merged_objects ligand1

Since:
    1.0.0

See Also:
    merge_to_group, merge_to_objects
```

</details>

### `merge_to_group`

Merge a structure into every object in a group

- **Usage:** `merge_to_group <group_name> <struct_name> [new_group_name='']`
- **Since:** 1.0.0
- **Tags:** `group`, `merge`, `combine`
- **See also:** `merge_to_objects`, `list_merged_objects`

**Examples:**

```
merge_to_group my_objects, ligand1
merge_to_group proteins, cofactor, merged_proteins
```

<details><summary>Full docstring</summary>

```
Merge *struct_name* into every object in *group_name*.

For each member object ``obj``, creates ``<obj>_with_<struct_name>`` by
unioning the two selections, then collects the new objects into
*new_group_name*.

Args:
    group_name: Name of the group whose members are the merge targets.
    struct_name: Name of the structure to merge into each target.
    new_group_name: Name for the result group.  Defaults to
        ``merge_to_<struct_name>``.

Returns:
    List of successfully created merged object names.

Examples:
    PyMOL> merge_to_group my_objects, ligand1
    PyMOL> merge_to_group proteins, cofactor, merged_proteins

Since:
    1.0.0

See Also:
    merge_to_objects, list_merged_objects
```

</details>

### `merge_to_objects`

Merge a structure into specific objects

- **Usage:** `merge_to_objects <object_names> <struct_name> [new_group_name='']`
- **Since:** 1.0.0
- **Tags:** `group`, `merge`, `combine`, `objects`
- **See also:** `merge_to_group`, `list_merged_objects`

**Examples:**

```
merge_to_objects obj1,obj2,obj3, ligand1
merge_to_objects protein1,protein2, cofactor, merged_proteins
```

<details><summary>Full docstring</summary>

```
Merge *struct_name* into a specific set of objects.

Args:
    object_names: Comma-separated object names to use as merge targets.
    struct_name: Name of the structure to merge into each target.
    new_group_name: Name for the result group.  Defaults to
        ``merge_to_<struct_name>``.

Returns:
    List of successfully created merged object names.

Examples:
    PyMOL> merge_to_objects obj1,obj2,obj3, ligand1
    PyMOL> merge_to_objects protein1,protein2, cofactor, merged_proteins

Since:
    1.0.0

See Also:
    merge_to_group, list_merged_objects
```

</details>

### `sort_all_groups`

Sort objects in every PyMOL group alphabetically

- **Usage:** `sort_all_groups`
- **Since:** 1.0.0
- **Tags:** `group`, `sort`, `order`, `batch`
- **See also:** `sort_group_objects`

**Examples:**

```
sort_all_groups
```

<details><summary>Full docstring</summary>

```
Sort objects in every PyMOL group alphabetically.

Returns:
    Dict mapping group name to the sorted object list for that group.
    Groups that failed or were skipped are not included.

Examples:
    PyMOL> sort_all_groups

Since:
    1.0.0

See Also:
    sort_group_objects
```

</details>

### `sort_group_objects`

Sort all objects within a group alphabetically

- **Usage:** `sort_group_objects <group_name>`
- **Since:** 1.0.0
- **Tags:** `group`, `sort`, `order`
- **See also:** `sort_all_groups`, `group_info`, `create_sorted_group`

**Examples:**

```
sort_group_objects my_proteins
sort_group_objects structures_group
```

<details><summary>Full docstring</summary>

```
Sort all objects within a group alphabetically (case-insensitive).

Removes objects from the group one-by-one then re-adds them in sorted
order.  Object data is not modified — only the group membership order
changes.

Args:
    group_name: Name of an existing PyMOL group.

Returns:
    The sorted list of object names, or an empty list when the group does
    not exist or contains fewer than two objects.

Examples:
    PyMOL> sort_group_objects my_proteins
    PyMOL> sort_group_objects structures_group

Since:
    1.0.0

See Also:
    sort_all_groups, group_info, create_sorted_group
```

</details>
