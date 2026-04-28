# PyMOLish

A curated PyMOL Open Source command extension library — organized by category, with a central command registry, standardized docs, intelligent autocompletion, and optional PyQt GUI panels.

## What is PyMOLish?

PyMOLish is an extension plugin for [PyMOL Open Source](https://github.com/schrodinger/pymol-open-source) that adds 54+ high-level commands grouped into I/O, groups, structure analysis, selection, visualization, and animation. Everything is registered through a single command registry, so discovery, help, and autocompletion work uniformly across the whole library.

It is meant to replace the repetitive scripting most PyMOL users end up writing by hand. With PyMOLish you can batch-load a directory of structures into a named group, run multi-alignment and report RMSDs, cluster ligands by position, fetch all PDB entries for a UniProt accession, apply perceptual color palettes to a group, or script transparency animations — each as a single command with autocompletion and inline help.

## Features

- **54 commands** across 7 categories
- **Zero required dependencies** — heavy libraries (NumPy, Biopython, Matplotlib, PyQt5) are optional extras you install only if you need them
- **Intelligent autocompletion** for groups, files, formats, and selections
- **Built-in discovery** via `pymolish_list`, `pymolish_help`, `pymolish_search`
- **Standardized Google-style docstrings** with examples, tags, and see-also links
- **Optional PyQt5 GUI panels**
- **Python 3.10+** (tested through 3.14)

## Requirements

- PyMOL Open Source
- Python 3.10 or newer — the same interpreter PyMOL uses
- Optional (only needed for specific features): `numpy`, `matplotlib`, `biopython`, `requests`, `PyQt5`

## Installation

PyMOLish installs in two steps: first install the Python package into the interpreter PyMOL uses, then register it with PyMOL through the Plugin Manager.

### Step 1 — Install into PyMOL's Python environment

Identify the Python interpreter PyMOL is using. Inside PyMOL's command line, run:

```python
import sys; print(sys.executable)
```

Then install the package into that interpreter. Pick the extras you need:

```bash
# Minimal — core commands only
/path/to/pymol-python -m pip install -e .

# With everything (numpy, matplotlib, biopython, requests, PyQt5)
/path/to/pymol-python -m pip install -e ".[all]"

# Just what you need
/path/to/pymol-python -m pip install -e ".[numpy,biopython]"
```

Available extras: `numpy`, `matplotlib`, `biopython`, `gui` (PyQt5), `dev` (pytest + ruff), `all`.

From a source clone:

```bash
git clone <repo-url> pymolish
cd pymolish
/path/to/pymol-python -m pip install -e ".[all]"
```

### Step 2 — Load the plugin in PyMOL

**Recommended — Plugin Manager GUI:**

1. Open PyMOL
2. Go to **Plugin → Plugin Manager**
3. Switch to the **Install New Plugin** tab
4. Under **Install from Repository**, click **Add** and point to the `pymolish` package directory (or the `src/pymolish/` folder of your source checkout)
5. Restart PyMOL

**Alternative — manual copy:**

Copy or symlink the `src/pymolish/` directory into PyMOL's plugin directory (typically `~/.pymol/startup/` on Linux/macOS; the exact path is shown in Plugin Manager → Settings). Restart PyMOL.

**Verify the install:**

In PyMOL's command line, run `pymolish_version`. You should see the version number and a command count.

## Quick Start

A typical PyMOLish session in the PyMOL command line:

```pymol
# Load every structure from a folder into a new group
load_files /data/pdbs, group=mystructures

# Inspect what's in the group
group_info mystructures

# Cycle through the objects one at a time
group_next mystructures

# Color the whole group with a perceptual palette
color_group_with_palette mystructures, palette=viridis

# Export every object in the group as CIF
export_group mystructures, format=cif, outdir=/data/out

# Discover more commands
pymolish_list
pymolish_help color_group_with_palette
```

## Commands Overview

Seven categories, 54 commands. Each category below lists a few highlights; follow the reference link for the full list with arguments, examples, and see-also.

### I/O — 7 commands · [full reference](docs/commands/i_o.md)
Batch-load structure files and export groups to CIF, PDB, FASTA, or CSV.
- `load_files` — load all structures from a directory into a group
- `export_group` — export every object in a group to a chosen format
- `export_byres_to_csv` — dump per-residue data to CSV

### Groups — 18 commands · [full reference](docs/commands/groups.md)
Manipulate PyMOL object groups: toggle visibility, navigate, sort, copy, merge, extract chains.
- `group_toggle` — toggle visibility of objects in a group
- `group_next` / `group_previous` — step through group members one at a time
- `merge_to_group` — merge a structure into every object in a group

### Structure — 8 commands · [full reference](docs/commands/structure.md)
Multi-alignment, cleanup, ligand clustering, and UniProt fetch.
- `multialign` — align multiple structures and report RMSD
- `cluster_ligands_by_position` — cluster ligands by 3D centroid (kmeans / hierarchical / distance)
- `fetch_by_uniprot` — fetch PDB entries for a UniProt accession

### Selection — 1 command · [full reference](docs/commands/selection.md)
Sequence-based selection helpers.
- `search_sequence` — find residues matching an amino-acid sequence via alignment

### Visualization — 6 commands · [full reference](docs/commands/visualization.md)
Color palettes, group coloring, and secondary-structure coloring.
- `color_group_with_palette` — apply an extended palette across a group
- `color_group_with_gradient` — single-color gradient across a group (needs matplotlib)
- `color_secondary_structure` — color helices, sheets, and loops

### Animation — 9 commands · [full reference](docs/commands/animation.md)
Transparency animations and group-cycling movies.
- `movie_transparency` — linear transparency animation over a frame range
- `fade_in` / `fade_out` — quick transparency fades
- `movie_from_group` — build a movie by cycling through group objects

### Meta — 5 commands · [full reference](docs/commands/meta.md)
Discovery and help, always available.
- `pymolish_list` — list commands by category
- `pymolish_help` — detailed help for a command
- `pymolish_search` — search by name, description, or tag

## Documentation

- [Command reference](docs/commands/README.md) — full auto-generated reference for all 54 commands
- [ARCHITECTURE_PLAN.md](ARCHITECTURE_PLAN.md) — design decisions, patterns, docstring template
- [CLAUDE.md](CLAUDE.md) — project conventions (useful if you plan to contribute)

## License

BSD-2-Clause — see [LICENSE](LICENSE).
