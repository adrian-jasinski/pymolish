# PyMOLish

Curated PyMOL Open Source command extension library — organized by category with a central command registry, standardized docs, intelligent autocompletion, and optional PyQt GUI panels.

## Project Structure

```
src/pymolish/
  __init__.py              # __init_plugin__(app), version, lazy bootstrap
  core/
    registry.py            # CommandRegistry singleton + CommandInfo dataclass
    autocompletion.py      # AutocompletionRegistry (cmd.auto_arg integration)
    types.py               # Shared type definitions, enums
    logging.py             # plog() — unified [pymolish] console output
    validators.py          # Common argument validators (dir, suffix, group, selection)
    group_utils.py         # GroupUtils — shared PyMOL group/object helpers
  extensions/              # Command modules, one sub-package per category
    io/                    # File Loading & Export (load_files, export_group, export_byres)
    groups/                # Group Operations (toggle, navigate, sort, copy, merge, extract_chain)
    structure/             # Structure Analysis (multialign, clean, cluster_ligands, fetch_uniprot)
    selection/             # Selection Helpers (sequence_search)
    visualization/         # Color & Visualization (palettes, color_group, color_ss)
    animation/             # Movie & Animation (transparency, movie_group)
  gui/                     # Shared PyQt GUI infrastructure (base_dialog, widgets)
tests/                     # pytest with mocked pymol.cmd
docs/commands/             # Auto-generated command reference (one .md per category)
plans/                     # Structured plans (active/, research/, finalized/, templates/)
```

## Tech Stack

- **PyMOL Open Source** — Molecular visualization (cmd.extend for command registration)
- **PyQt5** — Optional GUI panels (via pymol.Qt)
- **Biopython** — Optional: UniProt fetching, sequence search
- **NumPy** — Optional: ligand clustering, alignment stats
- **Matplotlib** — Optional: gradient color generation
- **Ruff** — Linting and formatting
- **Hatchling** — Build backend

## Key Patterns

### Command Registration
All commands are registered through `CommandRegistry.instance().register()` — never call `cmd.extend()` directly in command modules. Each extension sub-package has its own `__init_plugin__()` that handles registration and autocompletion setup.

### Extension Module Rules
1. Module-level imports: only stdlib + `pymol.cmd`
2. Heavy deps (numpy, biopython) imported inside functions with helpful ImportError messages
3. Functions have complete Google-style docstrings following the standardized template
4. All PyMOL console output goes through `plog()` from `core/logging.py`
5. No `cmd.extend()` at module level — the registry handles it
6. No `print()` at module level — no "Ready!" messages on import
7. Functions return typed values, not just print

### Meta-Commands (pymolish_ prefix)
`pymolish_list`, `pymolish_help`, `pymolish_search`, `pymolish_categories`, `pymolish_version`

## Development

- **Format/lint**: `ruff check . && ruff format .`
- **Test**: `pytest tests/`
- **Install (dev)**: `pip install -e ".[dev]"`
- **Install (all extras)**: `pip install -e ".[all]"`
- **Python**: >=3.10

## Plan

Claude must manage all structured plans inside the `plans/` directory.

Rules:
1. New plans must be written to `plans/active/` or `plans/research/` as Markdown files where active directory is default and research is used when user asks.
2. Each plan should have a clear header, steps, expected outputs, and tags.
3. When a plan is completed, Claude must move the corresponding file into `plans/finalized/`.
4. Claude may not place plans in random directories — only inside `plans/`.
5. Claude may create plan templates under `plans/templates/` for repeated workflows.
6. Claude must reference plan filenames when discussing or updating them.

## Rules

- After modifying command modules or registry -> update `docs/commands/` with current commands, options, and usage examples
- After adding/removing commands -> update autocompletion registrations in the category's `__init__.py`
- Commit work when code changes are complete
- New command modules go in the appropriate `src/pymolish/extensions/<category>/` sub-package
- New shared utilities go in `src/pymolish/core/`
- GUI panels go in `src/pymolish/gui/` (shared) or `extensions/<category>/_gui.py` (category-specific)
- Use existing utilities from `core/group_utils.py`, `core/validators.py` before writing new ones
- Every registered command must include: category, description, examples, tags, see_also
- Docstrings must follow the standardized template (see ARCHITECTURE_PLAN.md Section 6)

## Restrictions

- Do not modify files inside `.venv/` or external libraries
- Do not write files outside this repository
- Do not call `cmd.extend()` directly — always go through `CommandRegistry`
- Do not add module-level `print()` statements — use `plog()` for runtime output
- Do not add required (non-optional) dependencies — heavy deps are optional extras
- Do not remove `uv.lock` or `pyproject.toml` without user instruction
