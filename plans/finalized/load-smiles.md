# Plan: `load_smiles` / `paste_smiles` — molecules from SMILES with RDKit conformers

Tags: io, smiles, rdkit, conformers, clipboard, optional-dependency

## Goal

Load a molecule into PyMOL from a SMILES string (or a `.smi` file), generating 3D
conformers. Conformers land either as separate objects grouped under one name
(default) or as states of a single object. Ctrl+V in the 3D viewer loads the
clipboard if it parses as a molecule.

## Research: how to get 3D from SMILES

| Option | Verdict |
|---|---|
| **RDKit** (`MolFromSmiles` → `AddHs` → `EmbedMultipleConfs(ETKDGv3)` → MMFF/UFF) | Chosen. Pure pip wheel on all platforms, best conformer generator, de-facto standard. |
| OpenBabel / pybel | Heavier native install, no multi-conformer API as clean as ETKDG. |
| PyMOL built-ins | No SMILES parser in PyMOL Open Source; `cmd.fab` is peptides only. |
| Web services (PubChem 3D, CACTUS) | Network dependency, single conformer, no control. |

Hand-off to PyMOL: `Chem.MolToMolBlock(mol, confId=cid)` → `cmd.read_molstr(block, name, state=i)`.
No temp files.

## Commands (`extensions/io/load_smiles.py`)

| Command | Args | Notes |
|---|---|---|
| `load_smiles` | `smiles, name=None, n_conformers=10, mode=objects\|states, seed=42` | `smiles` may be a path to a `.smi`/`.smiles`/`.txt` file (`SMILES [name]` per line). Default name: `cmd.get_unused_name("mol")` → `mol01`, `mol02`, ... |
| `paste_smiles` | `n_conformers=10, mode=objects` | Reads clipboard (Qt, tkinter fallback), checks `is_smiles`, calls `load_smiles` with defaults. Bound to `CTRL-V` in the viewer via `cmd.set_key`. |

- `mode=objects`: `name_1 … name_n` grouped under `name` (single conformer → plain `name`).
- `mode=states`: one object `name` with n states (`discrete=0`).
- `n_conformers` caps the count; ETKDG RMS pruning (0.5 Å) may return fewer — logged.
- SMILES detection for paste: single whitespace-free token and `Chem.MolFromSmiles` is not `None`.

## Dependency

- `rdkit` becomes an optional extra in `pyproject.toml` (`[rdkit]`, included in `[all]`).
- `core/deps.py` `EXTRAS["rdkit"]` so `pymolish_install_deps rdkit` works.
- Missing RDKit → `plog` error: `rdkit is required; install with: pymolish_install_deps rdkit`.

## Steps

1. `pyproject.toml`: extra + version bump.
2. `core/deps.py`: EXTRAS entry.
3. `extensions/io/load_smiles.py`: commands + helpers.
4. `extensions/io/__init__.py`: register, autocomplete (`mode`), `KEY_BINDINGS = {"CTRL-V": "paste_smiles"}`.
5. `tests/test_io/test_load_smiles.py` (real RDKit in dev venv; mocked `pymol.cmd`).
6. `uv run python scripts/generate_docs.py`.

## Expected output

```
PyMOL> load_smiles CC(=O)Oc1ccccc1C(=O)O, aspirin, 5
[pymolish] io.smiles: aspirin: 5 conformer(s) as objects
PyMOL> load_smiles c1ccccc1, mode=states
[pymolish] io.smiles: mol01: 10 conformer(s) as states
```
