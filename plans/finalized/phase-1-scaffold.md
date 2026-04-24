# Phase 1 — Scaffold

**Status:** active
**Source:** `ARCHITECTURE_PLAN.md` Section 12 (Migration Checklist — Phase 1)
**Tags:** scaffold, bootstrap, core, registry, packaging

## Goal

Stand up the empty package skeleton for `pymolish` v1.0.0 so Phase 2 (command migration) has a stable framework to build on. No domain commands are migrated in this phase — only the core framework, package layout, and test harness.

## Steps

1. **Directory structure** — create the tree from `ARCHITECTURE_PLAN.md` Section 3:
   - `src/pymolish/{core,extensions,gui}/`
   - `src/pymolish/extensions/{io,groups,structure,selection,visualization,animation}/`
   - `tests/`
   - `docs/commands/`

2. **Core framework modules** under `src/pymolish/core/`:
   - `types.py` — shared enums (log levels, category names) and type aliases
   - `logging.py` — `plog(tag, message, level)` unified console output
   - `validators.py` — `validate_directory`, `validate_suffix`, `validate_group_exists`, `validate_object_exists`, `validate_selection`, `coerce_bool`
   - `registry.py` — `CommandInfo` dataclass + `CommandRegistry` singleton with `register/unregister/get/list_commands/search/categories`
   - `autocompletion.py` — `AutocompletionRegistry` with per-category `register()` and `apply()` pushing to `cmd.auto_arg`
   - `group_utils.py` — `GroupUtils` class with shared PyMOL group/object helpers (placeholder methods wired to `pymol.cmd`)

3. **Top-level `src/pymolish/__init__.py`**:
   - Declare `__version__ = "1.0.0"`
   - Define `__init_plugin__(app=None)` that iterates extension sub-packages and calls each category's `__init_plugin__`
   - Register meta-commands (`pymolish_list`, `pymolish_help`, `pymolish_search`, `pymolish_categories`, `pymolish_version`)

4. **Extension sub-package stubs** — each category gets an `__init__.py` with a no-op `__init_plugin__(app=None)` so the top-level bootstrap is wired end-to-end. Leaving the actual command modules for Phase 2.

5. **GUI scaffold** — `src/pymolish/gui/{__init__.py, base_dialog.py, widgets.py}` as empty stubs that import-guard PyQt5.

6. **Test harness** — `tests/conftest.py` installs a `pymol` mock into `sys.modules` so commands and registry code can be imported without PyMOL present. Add a smoke test per core module.

7. **Packaging** — verify `pyproject.toml` has `[build-system]` hatchling backend and `[tool.hatch.build.targets.wheel]` pointing at `src/pymolish`. Existing optional-deps layout is already close to Section 10.

8. **Verification** — run `ruff check .`, `ruff format --check .`, and `pytest tests/` to confirm the scaffold is clean.

## Expected Outputs

- Clean, importable `pymolish` package with `__init_plugin__` wired end-to-end
- All core framework classes instantiable under a mocked `pymol.cmd`
- `pytest` green with smoke tests covering registry, autocompletion, logging, validators
- `ruff check` and `ruff format --check` clean

## Out of Scope

- Migrating any PoC domain commands (Phase 2)
- Writing docstrings to the full template (Phase 3)
- GUI dialog implementations beyond empty base classes (Phase 4)
- Auto-generated `docs/commands/` (Phase 3)
