# Phase 2 — Command Migration

**Status:** active
**Source:** `ARCHITECTURE_PLAN.md` Section 8 + Section 12 (Phase 2)
**Tags:** migration, commands, io, groups, structure, selection, visualization, animation

## Goal

Port PoC command modules from `pymol-plugins/src/pymolish/*.py` into the new
`src/pymolish/extensions/<category>/` layout established in Phase 1. Each
migrated module should:

1. Use `plog()` from `pymolish.core.logging` for all console output — no raw
   `print()`.
2. Register via `CommandRegistry.instance().register(...)` from the category's
   `__init__.py` — no `cmd.extend()` at module level.
3. Have no module-level side effects (no "Ready!" prints on import).
4. Use `GroupUtils` from `pymolish.core.group_utils` instead of the PoC's own
   `group_utils.py`.
5. Use validators from `pymolish.core.validators` where applicable
   (`validate_directory`, `validate_suffix`, `coerce_bool`).
6. Defer heavy optional deps (numpy, biopython, matplotlib) to function scope.
7. Follow the docstring template from `ARCHITECTURE_PLAN.md` Section 6
   (Google style; Args / Returns / Examples / Since / See Also).
8. Have autocompletion bindings registered in the category's `__init__.py`.

## Migration Order

Doing one category at a time, validating with ruff + pytest after each. The
plan below lists the migration order and the PoC source for each category.

### 1. I/O — `extensions/io/`
- PoC sources: `load_files.py`, `export_group.py`, `export_byres_to_csv.py`
- New modules: `load_files.py`, `export_group.py`, `export_byres.py`
- Commands: `load_files`, `load_recursive`, `list_loadable_files`,
  `export_group`, `export_objects`, `export_by_pattern`,
  `export_byres_to_csv`

### 2. Groups — `extensions/groups/`
- PoC sources: `group_toggle.py`, `group_navigate.py` / `navigate_group.py`,
  `sort_group_objects.py`, `copy_group.py`, `merge_to_group.py`,
  `extract_chain_from_group.py`
- New modules: `toggle.py`, `navigate.py`, `sort.py`, `copy.py`, `merge.py`,
  `extract_chain.py`

### 3. Structure — `extensions/structure/`
- PoC sources: `multialign.py`, `clean.py`, `cluster_ligands_by_position.py`,
  `fetch_by_uniprot.py`
- New modules: `multialign.py`, `clean.py`, `cluster_ligands.py`,
  `fetch_uniprot.py`

### 4. Selection — `extensions/selection/`
- PoC source: `sequence_search.py`
- New module: `sequence_search.py`

### 5. Visualization — `extensions/visualization/`
- PoC source: `extended_color_palettes.py` (contains palettes + color_group +
  color_ss)
- New modules: `palettes.py`, `color_group.py`, `color_ss.py` — split by
  concern

### 6. Animation — `extensions/animation/`
- PoC sources: `movie_transparency.py`, `movie_group.py`
- New modules: `transparency.py`, `movie_group.py`

## Check-in Points

Stop and check with the user after each category's migration + test pass so
they can validate the translation pattern before it spreads across the
codebase.

## Out of Scope

- Docstring polish beyond Google-style basics (Phase 3)
- `docs/commands/` auto-generation (Phase 3)
- GUI panels (Phase 4)
