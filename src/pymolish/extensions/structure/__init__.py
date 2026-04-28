"""Structure analysis extensions: multialign, clean, cluster_ligands, fetch_uniprot."""

from __future__ import annotations

from ...core.autocompletion import AutocompletionRegistry
from ...core.registry import CommandRegistry
from ...core.types import Category

CATEGORY = Category.STRUCTURE


def __init_plugin__(app: object | None = None) -> None:
    """Register structure-analysis commands and their autocompletions."""
    from .clean import remove_ions, remove_metals
    from .cluster_ligands import cluster_ligands_by_position, cluster_ligands_from_group
    from .fetch_uniprot import fetch_by_uniprot, list_uniprot_structures
    from .multialign import list_objects_with_prefix, multialign

    registry = CommandRegistry.instance()
    autocomplete = AutocompletionRegistry.instance()
    completers = autocomplete.completers

    # ------------------------------------------------------------------
    # multialign
    # ------------------------------------------------------------------
    registry.register(
        "multialign",
        multialign,
        category=CATEGORY,
        description=(
            "Align multiple structures to a reference and report RMSD statistics"
        ),
        examples=[
            "multialign my_structures, reference_protein",
            "multialign protein_*, template_1",
            "multialign Estrogen, 1A52",
            "multialign Estrogen, 1A52, 0",
        ],
        tags=["alignment", "rmsd", "structure", "multi"],
        see_also=["list_objects_with_prefix"],
    )

    registry.register(
        "list_objects_with_prefix",
        list_objects_with_prefix,
        category=CATEGORY,
        description="List PyMOL objects whose names start with a given prefix",
        examples=[
            "list_objects_with_prefix protein_",
            "list_objects_with_prefix chain_A",
            "list_objects_with_prefix",
        ],
        tags=["list", "objects", "prefix", "utility"],
        see_also=["multialign"],
    )

    # ------------------------------------------------------------------
    # clean
    # ------------------------------------------------------------------
    registry.register(
        "remove_ions",
        remove_ions,
        category=CATEGORY,
        description="Remove common small ions from a PyMOL selection",
        examples=[
            "remove_ions",
            "remove_ions protein_complex",
            "remove_ions chain A",
        ],
        tags=["cleanup", "ions", "remove", "structure"],
        see_also=["remove_metals"],
    )

    registry.register(
        "remove_metals",
        remove_metals,
        category=CATEGORY,
        description="Remove common metal atoms from a PyMOL selection",
        examples=[
            "remove_metals",
            "remove_metals my_protein",
            "remove_metals chain B",
        ],
        tags=["cleanup", "metals", "remove", "structure"],
        see_also=["remove_ions"],
    )

    # ------------------------------------------------------------------
    # cluster_ligands
    # ------------------------------------------------------------------
    registry.register(
        "cluster_ligands_by_position",
        cluster_ligands_by_position,
        category=CATEGORY,
        description=(
            "Cluster ligands by 3-D centroid into new PyMOL groups (requires numpy)"
        ),
        examples=[
            "cluster_ligands_by_position ligands, 3",
            "cluster_ligands_by_position hetero, 4, hierarchical, 15.0",
            "cluster_ligands_by_position drug_group, 2, distance, 10.0, my_clusters",
        ],
        tags=["clustering", "ligands", "spatial", "numpy", "groups"],
        see_also=["cluster_ligands_from_group"],
    )

    registry.register(
        "cluster_ligands_from_group",
        cluster_ligands_from_group,
        category=CATEGORY,
        description="Cluster ligands from a named PyMOL group (requires numpy)",
        examples=[
            "cluster_ligands_from_group my_ligands, 2",
            "cluster_ligands_from_group compounds, 5, hierarchical",
            "cluster_ligands_from_group drug_group, 3, distance, 12.0",
        ],
        tags=["clustering", "ligands", "groups", "numpy"],
        see_also=["cluster_ligands_by_position"],
    )

    # ------------------------------------------------------------------
    # fetch_uniprot
    # ------------------------------------------------------------------
    registry.register(
        "fetch_by_uniprot",
        fetch_by_uniprot,
        category=CATEGORY,
        description=(
            "Fetch PDB structures for a UniProt accession via RCSB/UniProt APIs "
            "(requires requests)"
        ),
        examples=[
            "fetch_by_uniprot P04637",
            "fetch_by_uniprot P38398, 5",
            "fetch_by_uniprot Q9Y6R4, 3, 0",
        ],
        tags=["fetch", "uniprot", "pdb", "network"],
        see_also=["list_uniprot_structures"],
    )

    registry.register(
        "list_uniprot_structures",
        list_uniprot_structures,
        category=CATEGORY,
        description=(
            "List PDB structures for a UniProt accession without loading them "
            "(requires requests)"
        ),
        examples=[
            "list_uniprot_structures P04637",
            "list_uniprot_structures P38398, 1",
            "list_uniprot_structures Q9Y6R4, 0",
        ],
        tags=["list", "uniprot", "pdb", "network"],
        see_also=["fetch_by_uniprot"],
    )

    # ------------------------------------------------------------------
    # Autocompletion
    # ------------------------------------------------------------------
    autocomplete.register("multialign", 0, completers.group_name, "group/selection")
    autocomplete.register("multialign", 1, completers.object_name, "target")

    autocomplete.register(
        "list_objects_with_prefix", 0, completers.object_name, "prefix"
    )

    autocomplete.register("remove_ions", 0, completers.object_name, "selection")
    autocomplete.register("remove_metals", 0, completers.object_name, "selection")

    autocomplete.register(
        "cluster_ligands_by_position", 0, completers.group_name, "group/selection"
    )
    autocomplete.register(
        "cluster_ligands_from_group", 0, completers.group_name, "group"
    )
