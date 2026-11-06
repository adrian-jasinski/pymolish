# Meta

_9 command(s). Generated from the command registry — do not edit by hand._

## Commands in this category

- [`pymolish_categories`](#pymolish_categories) — List categories with command counts
- [`pymolish_help`](#pymolish_help) — Print detailed help for a registered command
- [`pymolish_install_deps`](#pymolish_install_deps) — Install optional dependencies into PyMOL's Python (pip or uv)
- [`pymolish_list`](#pymolish_list) — List all registered commands, optionally filtered by category
- [`pymolish_logo`](#pymolish_logo) — Show or hide the PyMOLish logo + version overlay in the viewer
- [`pymolish_reload`](#pymolish_reload) — Reload pymolish in place (after installing a new plugin ZIP)
- [`pymolish_search`](#pymolish_search) — Search commands by name, description, or tags
- [`pymolish_upgrade`](#pymolish_upgrade) — Install the newest plugin ZIP from GitHub and offer to reload
- [`pymolish_version`](#pymolish_version) — Show pymolish version and number of loaded commands

---

### `pymolish_categories`

List categories with command counts

- **Usage:** `pymolish_categories`
- **Since:** 0.1.25
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
- **Since:** 0.1.25
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
- **Since:** 0.1.25
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
        ``biopython``, ``rdkit``, ``gui``, or ``all`` (everything except ``gui``).
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
- **Since:** 0.1.25
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

### `pymolish_logo`

Show or hide the PyMOLish logo + version overlay in the viewer

- **Usage:** `pymolish_logo [show='toggle']`
- **Since:** 0.1.25
- **Tags:** `meta`, `logo`, `overlay`

**Examples:**

```
pymolish_logo
pymolish_logo 0
pymolish_logo toggle
```

<details><summary>Full docstring</summary>

```
Show or hide a PyMOLish logo + version overlay in the viewer.

The overlay is drawn via PyMOL's wizard prompt (top-left of the 3D view),
so it stays fixed on screen while the scene rotates.

Args:
    show: ``1``/``on`` to show, ``0``/``off`` to hide, ``toggle`` (default)
        to flip the current state.

Returns:
    ``True`` if the overlay is visible after the call, ``False`` otherwise.

Examples:
    pymolish_logo
    pymolish_logo 0

Since:
    0.1.25

See Also:
    pymolish_version
```

</details>

### `pymolish_reload`

Reload pymolish in place (after installing a new plugin ZIP)

- **Usage:** `pymolish_reload`
- **Since:** 0.1.25
- **Tags:** `meta`, `upgrade`, `reload`

**Examples:**

```
pymolish_reload
```

<details><summary>Full docstring</summary>

```
Reload pymolish in place and re-register every command.

Drops all ``pymolish`` modules from ``sys.modules``, imports the package
again from disk and runs its ``__init_plugin__``. Loaded objects and the
PyMOL session are untouched. Use this after installing a new plugin ZIP
without restarting PyMOL.

Returns:
    The version string of the freshly loaded package.

Examples:
    PyMOL> pymolish_reload

Since:
    0.1.23

See Also:
    pymolish_upgrade, pymolish_version
```

</details>

### `pymolish_search`

Search commands by name, description, or tags

- **Usage:** `pymolish_search <term>`
- **Since:** 0.1.25
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

### `pymolish_upgrade`

Install the newest plugin ZIP from GitHub and offer to reload

- **Usage:** `pymolish_upgrade [check_only=False] [restart=None]`
- **Since:** 0.1.25
- **Tags:** `meta`, `upgrade`, `update`

**Examples:**

```
pymolish_upgrade
pymolish_upgrade check_only=1
```

<details><summary>Full docstring</summary>

```
Upgrade pymolish from the newest ZIP in the GitHub ``plugin/`` folder.

Lists ``plugin/pymolish_<x>_<y>_<z>.zip`` files on GitHub, and when one is
newer than the running version downloads it and replaces the installed
package (only when pymolish was installed through PyMOL's Plugin Manager;
pip/uv installs and symlinked dev checkouts are refused). Afterwards a
yes/no dialog offers to reload the plugin in place; declining leaves the
old code running until you run ``pymolish_reload`` or restart PyMOL.

Args:
    check_only: When truthy, only report whether a newer version exists.
    restart: Skip the dialog: ``1`` reloads right away, ``0`` never does.
        Also the fallback when no GUI dialog is available (``pymol -c``).

Returns:
    The newer version string when one was found, ``None`` otherwise.

Examples:
    PyMOL> pymolish_upgrade
    PyMOL> pymolish_upgrade check_only=1
    PyMOL> pymolish_upgrade restart=0

Since:
    0.1.23

See Also:
    pymolish_reload, pymolish_version
```

</details>

### `pymolish_version`

Show pymolish version and number of loaded commands

- **Usage:** `pymolish_version`
- **Since:** 0.1.25
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
