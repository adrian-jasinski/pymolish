# PyMOLish — Architecture Plan

## 1. Project Vision

**PyMOLish** (package name `pymolish`) is a curated library of PyMOL Open Source terminal command extensions, organized by category, with a central command registry, standardized documentation, intelligent autocompletion, and optional PyQt GUI panels. It builds on the proven patterns from the PyMOLish PoC (v0.2.0, 33+ commands) while introducing cleaner separation of concerns, a plugin-per-category architecture, and a proper Python packaging story.

---

## 2. Key Design Decisions

### 2.1 Extension mechanism: `cmd.extend` (primary) + `__init_plugin__` (entry point)

Every command is registered via `cmd.extend()` through the central registry. The top-level `__init_plugin__(app)` is the single PyMOL plugin entry point that bootstraps everything. PyQt GUI panels are optional per-category add-ons — the commands always work headlessly from the PyMOL terminal.

### 2.2 Naming

The project keeps the **PyMOLish** brand (repo name `pymolish`, package name `pymolish`). The command prefix for registry meta-commands stays `pymolish_` (e.g., `pymolish_list`, `pymolish_help`). Individual domain commands keep short, descriptive names (e.g., `load_files`, `multialign`) to feel native to PyMOL.

### 2.3 Plugin loading strategy

PyMOL discovers plugins via `__init_plugin__` in packages placed in the plugin search path. We use **lazy module imports** inside `__init_plugin__` to keep PyMOL startup fast — expensive dependencies (numpy, biopython, matplotlib) are only imported when a command is actually called.

---

## 3. Repository Structure

```
pymolish/
├── pyproject.toml                    # Build config (hatchling), metadata, deps
├── README.md
├── LICENSE                           # BSD-2-Clause (consistent with PyMOL ecosystem)
├── CHANGELOG.md
├── .pre-commit-config.yaml
├── .github/
│   └── workflows/
│       ├── lint.yml                  # Ruff lint + format check
│       └── test.yml                  # pytest (mocked cmd where needed)
│
├── src/
│   └── pymolish/
│       ├── __init__.py               # __init_plugin__(app), version, lazy bootstrap
│       │
│       ├── core/                     # Framework layer (no PyMOL domain logic)
│       │   ├── __init__.py
│       │   ├── registry.py           # CommandRegistry class
│       │   ├── autocompletion.py     # AutocompletionRegistry class
│       │   ├── types.py              # Shared type definitions, enums
│       │   ├── logging.py            # Unified [pymolish] logging helpers
│       │   ├── validators.py         # Common argument validators
│       │   └── group_utils.py        # GroupUtils (shared PyMOL group helpers)
│       │
│       ├── extensions/               # Command modules, one sub-package per category
│       │   ├── __init__.py           # Auto-discovers & registers all sub-packages
│       │   │
│       │   ├── io/                   # File Loading & Export
│       │   │   ├── __init__.py       # category __init_plugin__, registers commands
│       │   │   ├── load_files.py
│       │   │   ├── export_group.py
│       │   │   ├── export_byres.py
│       │   │   └── _gui.py           # Optional PyQt panel for batch load/export
│       │   │
│       │   ├── groups/               # Group Operations
│       │   │   ├── __init__.py
│       │   │   ├── toggle.py
│       │   │   ├── navigate.py
│       │   │   ├── sort.py
│       │   │   ├── copy.py
│       │   │   ├── merge.py
│       │   │   └── extract_chain.py
│       │   │
│       │   ├── structure/            # Structure Analysis & Manipulation
│       │   │   ├── __init__.py
│       │   │   ├── multialign.py
│       │   │   ├── clean.py
│       │   │   ├── cluster_ligands.py
│       │   │   └── fetch_uniprot.py
│       │   │
│       │   ├── selection/            # Selection Helpers
│       │   │   ├── __init__.py
│       │   │   ├── sequence_search.py
│       │   │   └── (future commands)
│       │   │
│       │   ├── visualization/        # Color & Visualization
│       │   │   ├── __init__.py
│       │   │   ├── palettes.py
│       │   │   ├── color_group.py
│       │   │   └── color_ss.py       # Secondary structure coloring
│       │   │
│       │   └── animation/            # Movie & Animation
│       │       ├── __init__.py
│       │       ├── transparency.py
│       │       └── movie_group.py
│       │
│       └── gui/                      # Shared PyQt GUI infrastructure
│           ├── __init__.py
│           ├── base_dialog.py        # Base dialog class with common patterns
│           └── widgets.py            # Reusable widgets (group picker, file browser)
│
├── tests/
│   ├── conftest.py                   # Shared fixtures, mock cmd module
│   ├── test_registry.py
│   ├── test_autocompletion.py
│   ├── test_io/
│   │   └── test_load_files.py
│   ├── test_groups/
│   │   └── test_toggle.py
│   └── ...
│
└── docs/
    ├── commands/                     # Auto-generated command reference (one .md per category)
    └── development.md                # Contributing guide
```

---

## 4. Core Framework

### 4.1 CommandRegistry (`core/registry.py`)

Evolves the PoC registry with these improvements:

```python
@dataclass
class CommandInfo:
    """Metadata for a registered command."""
    name: str
    function: Callable
    category: str
    description: str          # One-line summary
    usage: str                # Auto-generated or explicit
    examples: list[str]       # PyMOL terminal examples
    since: str                # Version introduced (e.g. "1.0.0")
    see_also: list[str]       # Related command names
    tags: list[str]           # Searchable tags
    module: str               # Source module path


class CommandRegistry:
    """Central registry for all pymolish commands."""

    _instance: ClassVar[Optional["CommandRegistry"]] = None  # singleton

    def __init_subclass__(cls): ...  # prevent subclassing

    @classmethod
    def instance(cls) -> "CommandRegistry":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def register(
        self,
        name: str,
        function: Callable,
        *,
        category: str,
        description: str,
        usage: str | None = None,
        examples: list[str] | None = None,
        since: str = "1.0.0",
        see_also: list[str] | None = None,
        tags: list[str] | None = None,
        auto_extend: bool = True,
    ) -> None: ...

    def unregister(self, name: str) -> None: ...

    # Query API
    def get(self, name: str) -> CommandInfo | None: ...
    def list_commands(self, category: str | None = None) -> list[CommandInfo]: ...
    def search(self, term: str) -> list[CommandInfo]: ...
    def categories(self) -> list[str]: ...
```

**Changes from PoC:**
- Singleton pattern (no accidental double-init)
- `CommandInfo` dataclass instead of raw dict
- Added `since`, `see_also`, `tags` fields for richer discovery
- `unregister()` for testing/hot-reload scenarios
- Keyword-only arguments to prevent positional argument mistakes

### 4.2 AutocompletionRegistry (`core/autocompletion.py`)

Carries over from PoC with one structural change: completions are registered alongside commands in each category's `__init__.py`, not in a single monolithic file. The `AutocompletionRegistry` class stays the same but `setup_plugin_autocompletion()` is removed — each extension sub-package sets up its own completions.

### 4.3 GroupUtils (`core/group_utils.py`)

Moved from top level to `core/` since it's shared infrastructure used by groups, io, visualization, and animation categories.

### 4.4 Logging (`core/logging.py`)

Replace ad-hoc `print(f"[pyMOLish]...")` with a tiny helper:

```python
def plog(tag: str, message: str, level: str = "info") -> None:
    """Unified logging with consistent prefix."""
    prefix = f"[pext:{tag}]"
    if level == "error":
        print(f"{prefix} ERROR: {message}")
    elif level == "warn":
        print(f"{prefix} WARNING: {message}")
    else:
        print(f"{prefix} {message}")
```

This keeps output scannable in the PyMOL console while being grep-friendly.

### 4.5 Validators (`core/validators.py`)

Common validation functions extracted from command modules:

```python
def validate_directory(path: str) -> Path: ...
def validate_suffix(suffix: str) -> str: ...
def validate_group_exists(group_name: str) -> bool: ...
def validate_object_exists(object_name: str) -> bool: ...
def validate_selection(selection: str) -> bool: ...
def coerce_bool(value: str | bool | int) -> bool: ...
```

---

## 5. Extension Sub-Package Convention

Each category under `extensions/` follows this pattern:

```python
# extensions/io/__init__.py

"""I/O extensions: batch file loading, export, format conversion."""

CATEGORY = "I/O"

def __init_plugin__(app=None):
    """Register all I/O commands."""
    from pymolish.core.registry import CommandRegistry
    from pymolish.core.autocompletion import AutocompletionRegistry

    registry = CommandRegistry.instance()
    autocomplete = AutocompletionRegistry.instance()

    # Import commands lazily
    from .load_files import load_files, load_recursive, list_loadable_files
    from .export_group import export_group, export_objects, export_by_pattern
    from .export_byres import export_byres_to_csv

    # Register commands
    registry.register(
        "load_files",
        load_files,
        category=CATEGORY,
        description="Load multiple files from a directory with group management",
        examples=[
            "load_files",
            "load_files /tmp, sdf",
            "load_files ., pdb, my_proteins",
        ],
        tags=["batch", "load", "directory", "files"],
        see_also=["load_recursive", "list_loadable_files"],
    )
    # ... more registrations ...

    # Register autocompletions
    autocomplete.register("load_files", 0, autocomplete.completers.directory, "directory")
    autocomplete.register("load_files", 1, autocomplete.completers.format, "suffix")
    # ...
    autocomplete.apply()  # Push to cmd.auto_arg
```

**Rules for command modules** (e.g., `load_files.py`):

1. Module-level imports: only stdlib + `pymol.cmd`
2. Heavy deps (numpy, biopython) imported inside functions
3. Functions have complete Google-style docstrings
4. Functions return typed values (not just print)
5. All PyMOL console output goes through `plog()`
6. No `cmd.extend()` at module level — registry handles it
7. No `print()` at module level (no "Ready!" messages on import)

---

## 6. Standardized Command Documentation

Every command function must have a docstring following this template:

```python
def load_files(
    dir_name: str = ".",
    suffix: str = "pdb",
    group_name: str | None = None,
    prefix: str = "",
    name_filter: str | None = None,
    recursive: bool = False,
    exclude_subdirs: str | list[str] | None = None,
    max_depth: int = 3,
    verbose: bool = True,
) -> list[str]:
    """Load multiple structure files from a directory into PyMOL.

    Scans a directory for files matching the given suffix, loads each as a
    PyMOL object, and optionally groups them. Handles naming conflicts by
    appending numeric suffixes.

    Args:
        dir_name: Directory path to load from. Defaults to current directory.
        suffix: File extension without dot (e.g., "pdb", "cif", "sdf").
        group_name: If provided, loaded objects are placed in this group.
        prefix: String prepended to each object name.
        name_filter: Wildcard pattern for filename filtering (e.g., "model_*").
        recursive: Search subdirectories when True.
        exclude_subdirs: Subdirectory names to skip (comma-separated string or list).
        max_depth: Maximum directory depth for recursive search.
        verbose: Print progress to PyMOL console.

    Returns:
        List of successfully loaded object names.

    Examples:
        PyMOL> load_files
        PyMOL> load_files /data, cif, my_structures
        PyMOL> load_files ., pdb, , , model_*

    Since:
        1.0.0

    See Also:
        load_recursive, list_loadable_files, export_group
    """
```

**Documentation is auto-extractable**: a build script can generate `docs/commands/*.md` from the registry + docstrings.

---

## 7. Meta-Commands (Registry CLI)

The user-facing registry commands use the `pymolish_` prefix:

| Command | Description |
|---------|-------------|
| `pymolish_list [category]` | List all commands, optionally filtered by category |
| `pymolish_help <command>` | Detailed help for a command (docstring + examples) |
| `pymolish_search <term>` | Search commands by name, description, or tags |
| `pymolish_categories` | List all categories with command counts |
| `pymolish_version` | Show version and loaded extension count |

---

## 8. Command Categories & Migration Plan

Commands migrated from PoC, reorganized into the new structure:

### 8.1 I/O (File Loading & Export) — `extensions/io/`

| PoC Command | New Location | Changes |
|-------------|-------------|---------|
| `load_files` | `io/load_files.py` | Extract `_generate_unique_name`, `_create_group` to core utils |
| `load_recursive` | `io/load_files.py` | Merge with `load_files(recursive=True)` — keep as alias |
| `list_loadable_files` | `io/load_files.py` | Keep as-is |
| `export_group` | `io/export_group.py` | Keep |
| `export_objects` | `io/export_group.py` | Keep |
| `export_by_pattern` | `io/export_group.py` | Keep |
| `export_byres_to_csv` | `io/export_byres.py` | Keep |

### 8.2 Groups — `extensions/groups/`

| PoC Command | New Location | Changes |
|-------------|-------------|---------|
| `group_enable` | `groups/toggle.py` | Keep |
| `group_disable` | `groups/toggle.py` | Keep |
| `group_toggle` | `groups/toggle.py` | Keep |
| `group_status` | `groups/toggle.py` | Keep |
| `group_next` | `groups/navigate.py` | Keep |
| `group_previous` | `groups/navigate.py` | Keep |
| `sort_group_objects` | `groups/sort.py` | Keep |
| `sort_all_groups` | `groups/sort.py` | Keep |
| `group_info` | `groups/sort.py` | Keep |
| `create_sorted_group` | `groups/sort.py` | Keep |
| `copy_group` | `groups/copy.py` | Keep |
| `copy_group_objects` | `groups/copy.py` | Keep |
| `list_group_copies` | `groups/copy.py` | Keep |
| `merge_to_group` | `groups/merge.py` | Keep |
| `merge_to_objects` | `groups/merge.py` | Keep |
| `list_merged_objects` | `groups/merge.py` | Keep |
| `extract_chain_from_group` | `groups/extract_chain.py` | Keep |
| `extract_chains_from_group` | `groups/extract_chain.py` | Keep |

### 8.3 Structure Analysis — `extensions/structure/`

| PoC Command | New Location | Changes |
|-------------|-------------|---------|
| `multialign` | `structure/multialign.py` | Keep |
| `list_objects_with_prefix` | `structure/multialign.py` | Keep |
| `remove_ions` | `structure/clean.py` | Keep |
| `remove_metals` | `structure/clean.py` | Keep |
| `cluster_ligands_by_position` | `structure/cluster_ligands.py` | Keep |
| `cluster_ligands_from_group` | `structure/cluster_ligands.py` | Keep |
| `fetch_by_uniprot` | `structure/fetch_uniprot.py` | Keep |
| `list_uniprot_structures` | `structure/fetch_uniprot.py` | Keep |

### 8.4 Selection Helpers — `extensions/selection/`

| PoC Command | New Location | Changes |
|-------------|-------------|---------|
| `search_sequence` | `selection/sequence_search.py` | Keep |

*Future candidates: select_by_bfactor, select_interface, select_buried, expand_selection*

### 8.5 Visualization — `extensions/visualization/`

| PoC Command | New Location | Changes |
|-------------|-------------|---------|
| `register_extended_colors` | `visualization/palettes.py` | Keep |
| `list_available_palettes` | `visualization/palettes.py` | Keep |
| `color_group_with_palette` | `visualization/color_group.py` | Keep |
| `color_group_with_gradient` | `visualization/color_group.py` | Keep |
| `color_secondary_structure` | `visualization/color_ss.py` | Keep |
| `list_cartoon_palettes` | `visualization/color_ss.py` | Keep |

### 8.6 Animation — `extensions/animation/`

| PoC Command | New Location | Changes |
|-------------|-------------|---------|
| `movie_transparency` | `animation/transparency.py` | Keep |
| `fade_in` | `animation/transparency.py` | Keep |
| `fade_out` | `animation/transparency.py` | Keep |
| `transparency_pulse` | `animation/transparency.py` | Keep |
| `suggest_transparency_type` | `animation/transparency.py` | Keep |
| `set_frame_transparency` | `animation/transparency.py` | Keep |
| `transparency_sequence` | `animation/transparency.py` | Keep |
| `transparency_range` | `animation/transparency.py` | Keep |
| `movie_from_group` | `animation/movie_group.py` | Keep |

---

## 9. PyQt GUI Strategy

GUIs are **optional** and **per-category**. Each extension sub-package may contain a `_gui.py` module with a PyQt dialog. The naming convention with underscore prefix signals it's internal/optional.

GUI dialogs are registered as Plugin menu items only if PyQt is available:

```python
# In extensions/io/__init__.py, inside __init_plugin__:
try:
    from pymol.plugins import addmenuitemqt
    addmenuitemqt("Batch Load/Export", lambda: _show_io_gui())
except ImportError:
    pass  # PyQt not available — terminal commands still work
```

Shared GUI infrastructure in `gui/`:
- `BaseExtensionDialog` — common dialog scaffold (title, icon, close behavior, global reference caching)
- Reusable widgets: group picker combo, file/directory browser, object multi-select

---

## 10. Packaging & Installation

### pyproject.toml

```toml
[project]
name = "pymolish"
version = "1.0.0"
description = "Curated PyMOL command extensions for structural biology workflows"
requires-python = ">=3.10"
license = {text = "BSD-2-Clause"}
authors = [{name = "Adrian Jasinski"}]
dependencies = []  # Core has zero required deps

[project.optional-dependencies]
bio = ["biopython>=1.83"]        # fetch_uniprot, sequence_search
analysis = ["numpy>=1.20.0"]     # cluster_ligands, multialign stats
viz = ["matplotlib>=3.3.0"]      # gradient generation
all = ["pymolish[bio,analysis,viz]"]  # self-referencing extras
dev = ["pytest", "ruff", "pre-commit"]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/pymolish"]
```

**Key design choice**: zero required dependencies for core. Commands that need numpy/biopython check at call-time and give a helpful error:

```python
def fetch_by_uniprot(uniprot_id, ...):
    try:
        from Bio import ExPASy, SwissProt
    except ImportError:
        plog("fetch", "biopython is required: pip install pymolish[bio]", "error")
        return
```

### Installation methods

1. **pip install** (recommended): `pip install pymolish[all]`
2. **PyMOL Plugin Manager**: download ZIP from GitHub, install via Plugin > Install New Plugin
3. **Development**: `pip install -e ".[dev]"` from a clone of the repo

---

## 11. Testing Strategy

- **Unit tests**: mock `pymol.cmd` to test command logic without running PyMOL
- **Registry tests**: verify registration, search, category listing
- **Autocompletion tests**: verify `cmd.auto_arg` is populated correctly
- **Integration tests** (manual/CI-optional): run inside PyMOL headless mode

```python
# tests/conftest.py
import sys
from unittest.mock import MagicMock

# Mock pymol before any import
pymol_mock = MagicMock()
pymol_mock.cmd.get_names.return_value = []
pymol_mock.cmd.get_object_list.return_value = []
sys.modules["pymol"] = pymol_mock
sys.modules["pymol.cmd"] = pymol_mock.cmd
sys.modules["pymol.plugins"] = pymol_mock.plugins
```

---

## 12. Migration Checklist (PoC -> v1.0.0)

Phase 1 — Scaffold:
- [ ] Create repo with directory structure from Section 3
- [ ] Implement `core/registry.py` (CommandRegistry singleton + CommandInfo dataclass)
- [ ] Implement `core/autocompletion.py` (refactored from PoC)
- [ ] Implement `core/logging.py`, `core/validators.py`, `core/types.py`
- [ ] Move `group_utils.py` to `core/`
- [ ] Write top-level `__init__.py` with `__init_plugin__`
- [ ] Set up pyproject.toml, pre-commit, ruff config
- [ ] Write `tests/conftest.py` with PyMOL mocks

Phase 2 — Migrate commands (one category at a time):
- [ ] `extensions/io/` — load_files, export
- [ ] `extensions/groups/` — toggle, navigate, sort, copy, merge, extract
- [ ] `extensions/structure/` — multialign, clean, cluster, fetch
- [ ] `extensions/selection/` — sequence_search
- [ ] `extensions/visualization/` — palettes, color_group, color_ss
- [ ] `extensions/animation/` — transparency, movie_group

Phase 3 — Polish:
- [ ] Standardize all docstrings to template (Section 6)
- [ ] Replace all `print()` with `plog()`
- [ ] Remove module-level `print()` statements
- [ ] Add `since`, `see_also`, `tags` to all registrations
- [ ] Auto-generate `docs/commands/` from registry

Phase 4 — Extras:
- [ ] PyQt GUI panels for key categories (io, groups)
- [ ] GitHub Actions CI (lint + test)
- [ ] README with installation, usage, command reference
- [ ] First tagged release v1.0.0

---

## 13. Open Questions for Discussion

1. **Command naming prefix**: Should domain commands have a short prefix (e.g., `pymolish_load_files`) to avoid collisions with other plugins, or stay short (`load_files`) for ergonomics? Current plan: no prefix for domain commands, only `pymolish_` for meta-commands.

2. **Python version floor**: PoC requires 3.12+. Should we lower to 3.10 for broader PyMOL compatibility? The plan proposes 3.12.

3. **Config file**: Should there be a `~/.pymolish.toml` for user preferences (default verbose level, preferred palette, etc.)? Deferred to v1.1.

4. **Plugin sub-selection**: Should users be able to enable/disable specific categories? E.g., `PYMOLISH_DISABLE=animation,visualization`. Deferred to v1.1.
