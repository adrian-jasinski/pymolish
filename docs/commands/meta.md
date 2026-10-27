# Meta

_6 command(s). Generated from the command registry — do not edit by hand._

## Commands in this category

- [`pymolish_categories`](#pymolish_categories) — List categories with command counts
- [`pymolish_help`](#pymolish_help) — Print detailed help for a registered command
- [`pymolish_install_deps`](#pymolish_install_deps) — Install optional dependencies into PyMOL's Python (pip or uv)
- [`pymolish_list`](#pymolish_list) — List all registered commands, optionally filtered by category
- [`pymolish_search`](#pymolish_search) — Search commands by name, description, or tags
- [`pymolish_version`](#pymolish_version) — Show pymolish version and number of loaded commands

---

### `pymolish_categories`

List categories with command counts

- **Usage:** `pymolish_categories`
- **Since:** 0.1.12
- **Tags:** `meta`, `discovery`

**Examples:**

```
pymolish_categories
```

<details><summary>Full docstring</summary>

```
Print each category with the number of commands it contains.
```

</details>

### `pymolish_help`

Print detailed help for a registered command

- **Usage:** `pymolish_help <name>`
- **Since:** 0.1.12
- **Tags:** `meta`, `help`

**Examples:**

```
pymolish_help load_files
```

<details><summary>Full docstring</summary>

```
Print detailed help for a registered command.

Args:
    name: Command name, e.g. ``"load_files"``.

Returns:
    The :class:`CommandInfo` when found, ``None`` otherwise.
```

</details>

### `pymolish_install_deps`

Install optional dependencies into PyMOL's Python (pip or uv)

- **Usage:** `pymolish_install_deps [extras='all'] [dry_run=False]`
- **Since:** 0.1.12
- **Tags:** `meta`, `install`, `dependencies`

**Examples:**

```
pymolish_install_deps
pymolish_install_deps biopython
pymolish_install_deps numpy matplotlib, dry_run=1
```

<details><summary>Full docstring</summary>

```
Install optional pymolish dependencies into PyMOL's own Python.

Checks that the interpreter running PyMOL can ``import pymol`` (so the
packages land where PyMOL will find them), skips packages that are
already installed, then installs the rest with ``pip`` or, when pip is
missing (e.g. uv-managed venvs), ``uv pip install --python <python>``.

Args:
    extras: Comma- or space-separated extras: ``numpy``, ``matplotlib``,
        ``biopython``, ``gui``, or ``all`` (everything except ``gui``).
    dry_run: When truthy, only print the install command.

Returns:
    Pip requirements that were (or, with *dry_run*, would be) installed.

Examples:
    PyMOL> pymolish_install_deps
    PyMOL> pymolish_install_deps biopython
    PyMOL> pymolish_install_deps numpy matplotlib, dry_run=1

Since:
    0.1.11

See Also:
    pymolish_version
```

</details>

### `pymolish_list`

List all registered commands, optionally filtered by category

- **Usage:** `pymolish_list [category=None]`
- **Since:** 0.1.12
- **Tags:** `meta`, `discovery`

**Examples:**

```
pymolish_list
pymolish_list I/O
```

<details><summary>Full docstring</summary>

```
Print registered commands, optionally filtered by ``category``.

Returns:
    List of command names printed (useful for programmatic callers).
```

</details>

### `pymolish_search`

Search commands by name, description, or tags

- **Usage:** `pymolish_search <term>`
- **Since:** 0.1.12
- **Tags:** `meta`, `search`

**Examples:**

```
pymolish_search export
pymolish_search color
```

<details><summary>Full docstring</summary>

```
Search registered commands by ``term`` across names, descriptions, tags.
```

</details>

### `pymolish_version`

Show pymolish version and number of loaded commands

- **Usage:** `pymolish_version`
- **Since:** 0.1.12
- **Tags:** `meta`, `version`

**Examples:**

```
pymolish_version
```

<details><summary>Full docstring</summary>

```
Print the pymolish version and loaded command count.
```

</details>
