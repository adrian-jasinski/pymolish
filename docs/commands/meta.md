# Meta

_5 command(s). Generated from the command registry — do not edit by hand._

## Commands in this category

- [`pymolish_categories`](#pymolish_categories) — List categories with command counts
- [`pymolish_help`](#pymolish_help) — Print detailed help for a registered command
- [`pymolish_list`](#pymolish_list) — List all registered commands, optionally filtered by category
- [`pymolish_search`](#pymolish_search) — Search commands by name, description, or tags
- [`pymolish_version`](#pymolish_version) — Show pymolish version and number of loaded commands

---

### `pymolish_categories`

List categories with command counts

- **Usage:** `pymolish_categories`
- **Since:** 1.0.0
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
- **Since:** 1.0.0
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

### `pymolish_list`

List all registered commands, optionally filtered by category

- **Usage:** `pymolish_list [category=None]`
- **Since:** 1.0.0
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
- **Since:** 1.0.0
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
- **Since:** 1.0.0
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
