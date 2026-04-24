"""I/O extensions: batch file loading, export, residue CSV export."""

from __future__ import annotations

from pymolish.core.autocompletion import AutocompletionRegistry
from pymolish.core.registry import CommandRegistry
from pymolish.core.types import Category

CATEGORY = Category.IO


def __init_plugin__(app: object | None = None) -> None:
    """Register I/O commands and their autocompletions."""
    from .export_byres import export_byres_to_csv
    from .export_group import export_by_pattern, export_group, export_objects
    from .load_files import list_loadable_files, load_files, load_recursive

    registry = CommandRegistry.instance()
    autocomplete = AutocompletionRegistry.instance()
    completers = autocomplete.completers

    registry.register(
        "load_files",
        load_files,
        category=CATEGORY,
        description="Load structure files from a directory with optional grouping",
        examples=[
            "load_files",
            "load_files /tmp, sdf",
            "load_files ., pdb, my_proteins",
            "load_files ., pdb, proteins, loaded_",
            "load_files ., cif, , , model_*",
            "load_files ., pdb, , , , 1, traj",
        ],
        tags=["batch", "load", "directory", "files"],
        see_also=["load_recursive", "list_loadable_files", "export_group"],
    )

    registry.register(
        "load_recursive",
        load_recursive,
        category=CATEGORY,
        description="Recursively load structure files from a directory tree",
        examples=[
            "load_recursive",
            "load_recursive /data, sdf, ligands",
            "load_recursive ., cif, , , model_*",
            "load_recursive ., pdb, , , , 2",
        ],
        tags=["batch", "load", "recursive"],
        see_also=["load_files", "list_loadable_files"],
    )

    registry.register(
        "list_loadable_files",
        list_loadable_files,
        category=CATEGORY,
        description="Preview files that would be loaded without loading them",
        examples=[
            "list_loadable_files",
            "list_loadable_files /tmp, sdf, 1",
            "list_loadable_files ., cif, 0, model_*",
            "list_loadable_files ., pdb, 1, , traj",
        ],
        tags=["preview", "list", "directory"],
        see_also=["load_files", "load_recursive"],
    )

    registry.register(
        "export_group",
        export_group,
        category=CATEGORY,
        description="Export all objects in a group as CIF/PDB/FASTA files",
        examples=[
            "export_group my_structures",
            "export_group proteins, ., pdb",
            "export_group sequences, ., fasta",
            "export_group models, ./out, cif, 1",
        ],
        tags=["export", "group", "save"],
        see_also=["export_objects", "export_by_pattern", "export_byres_to_csv"],
    )

    registry.register(
        "export_objects",
        export_objects,
        category=CATEGORY,
        description="Export explicit PyMOL objects as CIF/PDB/FASTA files",
        examples=[
            "export_objects obj1,obj2,obj3",
            "export_objects obj1,obj2, ./out, pdb",
        ],
        tags=["export", "objects", "save"],
        see_also=["export_group", "export_by_pattern"],
    )

    registry.register(
        "export_by_pattern",
        export_by_pattern,
        category=CATEGORY,
        description="Export objects whose names match a wildcard pattern",
        examples=[
            "export_by_pattern protein_*",
            "export_by_pattern chain_*, ./out, pdb",
        ],
        tags=["export", "pattern", "save"],
        see_also=["export_group", "export_objects"],
    )

    registry.register(
        "export_byres_to_csv",
        export_byres_to_csv,
        category=CATEGORY,
        description="Write residues of a selection (chain, resname, resid) to CSV",
        examples=[
            "export_byres_to_csv protein, residues.csv",
            "export_byres_to_csv chain A, chain_a.csv",
            "export_byres_to_csv resi 1-50, residues_1_50.csv",
        ],
        tags=["export", "residues", "csv"],
        see_also=["export_group"],
    )

    autocomplete.register("load_files", 0, completers.directory, "directory")
    autocomplete.register("load_files", 1, completers.format, "suffix")
    autocomplete.register("load_files", 2, completers.group_name, "group")

    autocomplete.register("load_recursive", 0, completers.directory, "directory")
    autocomplete.register("load_recursive", 1, completers.format, "suffix")
    autocomplete.register("load_recursive", 2, completers.group_name, "group")

    autocomplete.register("list_loadable_files", 0, completers.directory, "directory")
    autocomplete.register("list_loadable_files", 1, completers.format, "suffix")

    autocomplete.register("export_group", 0, completers.group_name, "group")
    autocomplete.register("export_group", 1, completers.directory, "output_dir")
    autocomplete.register("export_group", 2, completers.format, "format")

    autocomplete.register("export_objects", 0, completers.object_name, "object")
    autocomplete.register("export_objects", 1, completers.directory, "output_dir")
    autocomplete.register("export_objects", 2, completers.format, "format")

    autocomplete.register("export_by_pattern", 1, completers.directory, "output_dir")
    autocomplete.register("export_by_pattern", 2, completers.format, "format")

    autocomplete.register("export_byres_to_csv", 0, completers.object_name, "selection")
