# Quick start

This walkthrough takes a folder of structures through loading, inspecting, aligning, coloring, and exporting. Every step is one command typed into PyMOL's command line. Press **Tab** after a command name to complete group names, file paths, and options.

If you have not installed PyMOLish yet, start with the [Installation guide](installation.md).

The [video tour](https://www.youtube.com/watch?v=q6c24OJZzd4&t=25s) shows the first part of this session live: fetching a structure, loading a set of ligands into a group with `load_files`, and stepping through them.

## Load a folder of structures into a group

PyMOL groups are the backbone of PyMOLish. Most commands work on a group, so the first step is to put related structures into one.

Typical inputs are docking results (many poses of the same ligand) or several PDB structures of the same protein. Each kind goes into its own group:

```pymol
# Docking poses, all .pdb files from one folder
load_files /data/docking/run1, pdb, poses

# Crystal structures of the protein of interest, as .cif
load_files /data/structures, cif, xtal

# SDF ligands, searched recursively up to three folders deep
load_recursive /data/ligands, sdf, ligands
```

The arguments are: folder, file suffix, group name. Use `name_filter` to pick only some files:

```pymol
load_files /data/docking/run1, pdb, best_poses, name_filter=rank0
```

Not sure what is in a folder? `list_loadable_files /data/docking/run1, pdb` prints what `load_files` would pick up, without loading anything.

## Look at what you loaded

```pymol
group_info poses        # members, count, whether they are sorted
group_status poses      # which members are currently shown
```

## Step through the structures one at a time

With many poses loaded, looking at them all at once is noise. Show one at a time:

```pymol
group_next poses        # show the next member, hide the rest
group_previous poses    # go back
```

The same two commands are bound to **CTRL-N** and **CTRL-P**, so you can keep your hands on the keyboard while you flip through poses. When only one group is loaded, the group name can be omitted.

To bring everything back:

```pymol
group_enable poses      # show all members
group_disable poses     # hide all members
group_toggle poses      # flip each member's visibility
```

## Keep the group tidy

```pymol
sort_group poses                 # alphabetical
sort_group poses, reverse=1      # reverse alphabetical
copy_group poses, poses_backup   # duplicate the group and its members
```

## Color the group

Give every member its own color from a palette:

```pymol
color_group_with_palette poses, pastels
color_group_with_palette xtal, ocean
list_available_palettes          # pastels, neon, earth, ocean, warm, cool
```

Or shade them with a gradient of a single color:

```pymol
color_group_with_gradient poses, blue
```

Secondary structure coloring for a single object:

```pymol
color_secondary_structure xtal_1abc, palette=ard
list_cartoon_palettes
```

## Align everything to a reference

```pymol
multialign poses, reference_pose
```

Aligns each member of the group to the reference and prints the RMSD per member.

## Clean up

```pymol
water                   # hide waters in everything
water on                # show them again
ions                    # same for ions
remove_ions xtal_1abc   # delete ions from one object
remove_metals           # delete metals everywhere
```

## Cluster ligands by position

When poses are stored as separate objects, find out how many distinct binding modes there are. Needs NumPy (`pymolish_install_deps numpy`).

```pymol
cluster_ligands_from_group poses, 3                   # k-means, 3 clusters
cluster_ligands_from_group poses, 5, hierarchical
cluster_ligands_from_group poses, 3, distance, 8.0   # distance cutoff in Å
```

Each cluster becomes a new group, `ligand_cluster_1`, `ligand_cluster_2`, …, so you can step through them with `group_next`.

## Pull structures from UniProt

Have an accession but not the files? These commands query the RCSB and UniProt web services, so you need a network connection but no extra packages.

```pymol
list_uniprot_structures P04637         # what is available
fetch_by_uniprot P04637, 5             # load the first 5 PDB entries
fetch_uniprot_ligands P04637           # load every distinct ligand bound in those entries
```

## Export the results

```pymol
export_group poses, /data/out, cif            # one file per member
export_group poses, /data/out, pdb
export_group xtal, /data/out, fasta           # sequences
export_byres_to_csv poses_rank1, pose1.csv    # per-residue table
```

## Find other commands

```pymol
pymolish_list                      # everything, grouped by category
pymolish_list Groups               # one category
pymolish_search chain              # by keyword
pymolish_help extract_chain_from_group
```

The full reference with every argument is in [docs/commands](commands/README.md).
