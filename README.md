<p align="center"><img src="img/logo.png" alt="PyMOLish logo" width="300"></p>

# PyMOLish

Extra commands for [PyMOL Open Source](https://github.com/schrodinger/pymol-open-source) that take the repetitive scripting out of everyday structure work.

Load a folder of docking poses into one group, align them to a reference and get the RMSDs, cluster ligands by where they sit, fetch every PDB entry for a UniProt accession, color a whole group with one palette — each of these is a single command with tab completion and built-in help.

## Highlights

- **49 commands** in six categories: I/O, groups, structure analysis, selection, visualization, and discovery/help
- **Works out of the box** — no required third-party packages. NumPy and Biopython are optional and only needed by three commands
- **Tab completion** for group names, files, formats, and selections
- **Built-in help** — `pymolish_list`, `pymolish_help <command>`, `pymolish_search <term>`
- **GUI integration** — new entries in the group right-click **A**ction menu, plus keyboard shortcuts for stepping through a group (more GUI features are planned)

Most commands are run from the PyMOL command line. A few of the group commands are also reachable from the GUI; see [GUI features](docs/gui.md).

## Requirements

- **PyMOL Open Source 3.0 or newer**
- **Python 3.10 or newer** — the interpreter PyMOL itself runs on
- Optional, only for specific commands: `numpy` (ligand clustering) and `biopython` (sequence search). Everything else, including UniProt fetching and gradient colors, uses only the standard library

If an optional package is missing, only the commands that need it are affected. They print what to install and leave the rest of the plugin working.

## Installation

The quick version:

1. Download a `pymolish_<version>.zip` from the [`plugin/`](plugin/) directory (or build your own with `python scripts/build_plugin.py`).
2. In PyMOL open **Plugin → Plugin Manager → Install New Plugin → Choose file…** and pick the ZIP.
3. Restart PyMOL and run `pymolish_version` in the command line.

Step-by-step instructions with screenshots, optional dependencies, and troubleshooting are in the **[Installation guide](docs/installation.md)**.

## Quick start

Say you have a folder of docking results — or several PDB structures of the same protein — and want to look at them side by side:

```pymol
# Load every .pdb from the folder into one group
load_files /data/docking_poses, pdb, poses

# What did we get?
group_info poses

# Step through the poses one at a time (or press CTRL-N / CTRL-P)
group_next poses

# Give each pose its own color
color_group_with_palette poses, pastels

# Align all poses to a reference and print the RMSDs
multialign poses, reference

# Save everything as CIF
export_group poses, /data/out, cif

# Find more commands
pymolish_list
pymolish_help load_files
```

A longer walkthrough, including ligand clustering and UniProt fetching, is in the **[Quick start guide](docs/quickstart.md)**.

## Documentation

| Guide | What it covers |
|-------|----------------|
| [Installation](docs/installation.md) | Installing the ZIP, building your own, optional dependencies, troubleshooting |
| [Quick start](docs/quickstart.md) | A worked session from loading files to exporting results |
| [GUI features](docs/gui.md) | Group action menu entries and keyboard shortcuts |
| [Command reference](docs/commands/README.md) | Every command with arguments and examples, by category |

### Command categories

| Category | Commands | What it does |
|----------|---------:|--------------|
| [I/O](docs/commands/i_o.md) | 7 | Batch-load structure files; export groups to CIF, PDB, FASTA, or CSV |
| [Groups](docs/commands/groups.md) | 18 | Toggle, navigate, sort, copy, merge groups; extract chains |
| [Structure](docs/commands/structure.md) | 9 | Multi-alignment, cleanup, ligand clustering, UniProt fetching |
| [Selection](docs/commands/selection.md) | 3 | Sequence search; show/hide/select waters and ions |
| [Visualization](docs/commands/visualization.md) | 6 | Color palettes, group coloring, secondary-structure coloring |
| [Meta](docs/commands/meta.md) | 6 | List, search, and get help on commands; install optional dependencies |

## For developers

```bash
git clone <repo-url> pymolish
cd pymolish
pip install -e ".[dev]"      # pytest + ruff
pytest tests/
ruff check . && ruff format .
python scripts/build_plugin.py   # -> plugin/pymolish_<x>_<y>_<z>.zip
```

## License

MIT — see [LICENSE](LICENSE).
