# Changelog

All notable changes to PyMOLish are documented here. Entries are grouped by
the version in `pyproject.toml`; the newest version is at the top.

## 0.1.25 — 2026-11-04

- Added `pymolish_logo` meta-command: show/hide a PyMOLish logo + version overlay in the viewer.

## 0.1.24 — 2026-11-04

- Added `load_smiles`: SMILES parsing and conformer generation via RDKit (also Ctrl+V paste).

## 0.1.23 — 2026-11-04

- Improved `fetch_fold`.
- Added option for automated plugin upgrades.
- Docs: added tutorial videos.

## 0.1.22 — 2026-11-03

- `fetch_fold` accepts AlphaFold IDs directly.
- Added coloring by AlphaFold confidence (pLDDT).

## 0.1.21 — 2026-11-03

- Added `fetch_fold`: download AlphaFold models.

## 0.1.20 — 2026-11-02

- UniProt downloads are placed in a named group.
- Synced `uv.lock` version.

## 0.1.19 — 2026-11-02

- Added UI scale command to enlarge fonts and buttons in PyMOL menus.

## 0.1.18 — 2026-10-29

- Fixed version update and version shown in the PyMOL plugin manager.
- Docs: readability pass; added GIF and tutorial video link.

## 0.1.17 — 2026-10-29

- Versioned plugin ZIP name (`pymolish_<x>_<y>_<z>.zip`) is now the default; added `--unversioned` to `build_plugin.py`.

## 0.1.16 — 2026-10-29

- Added `fetch_uniprot_ligands`: load all distinct ligands for a UniProt accession.
- Version is now defined only in `pyproject.toml`; `__version__` is derived from it.

## 0.1.14 — 2026-10-28

- Bound Ctrl-N / Ctrl-P to `group_next` / `group_previous`.
- Added `--versioned` flag to `build_plugin.py`.

## 0.1.13 — 2026-10-27

- Group Action menu entries moved next to PyMOL's own group rows (blue, `group` suffix).

## 0.1.12 — 2026-10-27

- Added water and ions selection commands with on/off show/hide modes.

## 0.1.11 — 2026-10-23

- Added `pymolish_install_deps` meta-command.

## 0.1.10 — 2026-10-23

- `fetch_by_uniprot` is dependency-free; Biopython is an optional fallback.
- README: added logo.

## 0.1.9 — 2026-10-22

- Group Action menu uses plain `sort` label.

## 0.1.8 — 2026-10-22

- Added PyMOLish entries to the PyMOL group Action (A) menu.

## 0.1.7 — 2026-10-16

- Removed animation commands.

## 0.1.5 — 2026-10-16

- Fixed Windows import errors.

## 0.1.4 — 2026-10-16

- Clearer optional-dependency failure messages; verified minimal installs.

## 0.1.3 — 2026-06-17

- Simplification pass over the codebase.

## 0.1.2 — 2026-06-17

- Updated group sorting; added version-bump rules.

## 0.1.0 — 2026-04-24

- Initial release: core registry, autocompletion, standardized docs and templates.
- Relative imports so PyMOLish loads as a PyMOL plugin.
