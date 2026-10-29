# PyMOLish command reference

Auto-generated from the command registry by `scripts/generate_docs.py`. Run `uv run python scripts/generate_docs.py` after editing commands.

## Commands Overview

Six categories. Each category below lists a few highlights; follow the reference link for the full list with arguments, examples, and see-also.

### I/O — 7 commands · [full reference](i_o.md)
Batch-load structure files and export groups to CIF, PDB, FASTA, or CSV.
- `load_files` — load all structures from a directory into a group
- `export_group` — export every object in a group to a chosen format
- `export_byres_to_csv` — dump per-residue data to CSV

### Groups — 18 commands · [full reference](groups.md)
Manipulate PyMOL object groups: toggle visibility, navigate, sort, copy, merge, extract chains.
- `group_toggle` — toggle visibility of objects in a group
- `group_next` / `group_previous` — step through group members one at a time
- `merge_to_group` — merge a structure into every object in a group

### Structure — 9 commands · [full reference](structure.md)
Multi-alignment, cleanup, ligand clustering, and UniProt fetch.
- `multialign` — align multiple structures and report RMSD
- `cluster_ligands_by_position` — cluster ligands by 3D centroid (kmeans / hierarchical / distance)
- `fetch_by_uniprot` — fetch PDB entries for a UniProt accession

### Selection — 3 commands · [full reference](selection.md)
Sequence search and quick show/hide for waters and ions.
- `search_sequence` — find residues matching an amino-acid sequence via alignment
- `water` / `ions` — show, hide, or select waters and ions in one word

### Visualization — 6 commands · [full reference](visualization.md)
Color palettes, group coloring, and secondary-structure coloring.
- `color_group_with_palette` — apply an extended palette across a group
- `color_group_with_gradient` — single-color gradient across a group
- `color_secondary_structure` — color helices, sheets, and loops

### Meta — 6 commands · [full reference](meta.md)
Discovery, help, and dependency setup, always available.
- `pymolish_list` — list commands by category
- `pymolish_help` — detailed help for a command
- `pymolish_search` — search by name, description, or tag
- `pymolish_install_deps` — install optional dependencies into PyMOL's Python