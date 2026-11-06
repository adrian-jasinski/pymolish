# Plan: SMILES file formats, object names, and parent groups

Status: completed (2026-11-06)
Tags: io, smiles, csv, naming, groups, optional-dependency

## Goal and scope

Extend the existing `load_smiles` command, preserving its first five positional
arguments and RDKit conformer behavior. Keep parsing and naming helpers local to
`extensions/io/load_smiles.py`; reuse `GroupUtils` for unique names and grouping.
The existing implementation already reads basic whitespace-separated files but
does not support CSV or parent groups and ignores a single file entry's label.

## Behavior

- Detect file input from an existing file or a `.smi`, `.smiles`, `.txt`, or
  `.csv` suffix (case-insensitive); otherwise interpret the input as SMILES.
  Support quoted paths and `~`. Report missing/unreadable files clearly.
- Read UTF-8 text (including a BOM). Text files use spaces or tabs; CSV files
  automatically use comma or semicolon delimiters and honor quoted fields.
  The first column always contains SMILES. Ignore blank lines, `#` comments,
  an optional initial `SMILES` header, and unused metadata columns.
- Append `group_name=None` and `name_column=2` to the command signature.
  `name_column` is one-based; `0` disables names from the file. The default
  preserves the existing use of the second column. Missing/empty labels fall
  back to `name` for one molecule, or unused names from the `name` prefix for
  multiple molecules (default: `mol`). File labels take precedence even for a
  one-molecule file. Inline input keeps `name` behavior.
- Normalize labels to legal PyMOL names and avoid overwriting existing objects,
  duplicate file labels, generated conformer names, or the requested parent
  group. Keep successful molecules when another entry has invalid SMILES.
- Add loaded molecule objects or their conformer subgroups to `group_name`.
  Reuse existing groups, reject collisions with non-group objects before loading,
  preserve conformer subgroups, and do not create empty groups on failure.
- Keep RDKit optional and CSV imports local, preserving plugin startup even in
  PyMOL runtimes missing the standard-library CSV extension.

## Steps and expected outputs

1. Implement detection/parsing, configurable naming, and parent grouping in the
   existing command. Output: working inline, whitespace-file, and CSV loads.
2. Add focused regressions using shared PyMOL mocks and existing RDKit support:
   formats, separators, quoting, headers, name columns, duplicate names,
   single-entry files, grouping in both modes, and failure paths.
3. Update registry metadata/examples and group completion without moving
   existing argument positions; regenerate and review command documentation.
4. Bump `pyproject.toml` from `0.1.25` to `0.1.26`, add newest-first changelog
   bullets, run the full pytest suite and Ruff checks, and build the plugin ZIP.
5. Record results and move this plan to `plans/finalized/`.

## Usage examples

```text
load_smiles CCO, ethanol, 1
load_smiles ligands.smi, group_name=ligands
load_smiles ligands.csv, group_name=screen, name_column=3
load_smiles ligands.txt, name=lig, name_column=0
```

## Results

- Implemented file detection, text/CSV parsing, configurable file names,
  collision protection, and optional parent grouping.
- Updated command metadata, examples, group completion, and generated I/O docs.
- Bumped the package to `0.1.26` and added the changelog entry.
- Focused tests: 65 passed, including plugin bootstrap and optional dependencies.
- Full suite: `.venv/bin/python -m pytest tests/` — 349 passed.
- `.venv/bin/ruff check .` and `.venv/bin/ruff format --check .` — passed.
- `git diff --check` — passed.
- Built `plugin/pymolish_0_1_26.zip` with `python3 scripts/build_plugin.py`.

## Verification limits

Tests exercise real RDKit and mocked PyMOL. A live PyMOL session is needed to
verify viewer integration and interactive completion.
