"""Group operation extensions: toggle, navigate, sort, copy, merge, extract."""

from __future__ import annotations

from ...core.autocompletion import AutocompletionRegistry
from ...core.registry import CommandRegistry
from ...core.types import Category

CATEGORY = Category.GROUPS


def __init_plugin__(app: object | None = None) -> None:
    """Register group-manipulation commands and their autocompletions."""
    from .copy import copy_group, copy_group_objects, list_group_copies
    from .extract_chain import extract_chain_from_group, extract_chains_from_group
    from .merge import list_merged_objects, merge_to_group, merge_to_objects
    from .navigate import group_next, group_previous
    from .sort import (
        create_sorted_group,
        group_info,
        sort_all_groups,
        sort_group_objects,
    )
    from .toggle import group_disable, group_enable, group_status, group_toggle

    registry = CommandRegistry.instance()
    autocomplete = AutocompletionRegistry.instance()
    completers = autocomplete.completers

    # ------------------------------------------------------------------ toggle
    registry.register(
        "group_enable",
        group_enable,
        category=CATEGORY,
        description="Enable objects in a group or matching a pattern",
        examples=[
            "group_enable my_group",
            "group_enable my_group, 2",
            "group_enable chain_*",
        ],
        tags=["group", "enable", "visibility"],
        see_also=["group_disable", "group_toggle", "group_status"],
    )

    registry.register(
        "group_disable",
        group_disable,
        category=CATEGORY,
        description="Disable objects in a group or matching a pattern",
        examples=[
            "group_disable my_group",
            "group_disable my_group, 2",
            "group_disable chain_*",
        ],
        tags=["group", "disable", "visibility"],
        see_also=["group_enable", "group_toggle", "group_status"],
    )

    registry.register(
        "group_toggle",
        group_toggle,
        category=CATEGORY,
        description="Toggle visibility of objects in a group or matching a pattern",
        examples=[
            "group_toggle my_group",
            "group_toggle my_group, 2",
        ],
        tags=["group", "toggle", "visibility"],
        see_also=["group_enable", "group_disable", "group_status"],
    )

    registry.register(
        "group_status",
        group_status,
        category=CATEGORY,
        description="Report enabled/disabled state of objects in a group or pattern",
        examples=[
            "group_status my_group",
            "group_status chain_*",
        ],
        tags=["group", "status", "visibility"],
        see_also=["group_enable", "group_disable", "group_toggle"],
    )

    # --------------------------------------------------------------- navigate
    registry.register(
        "group_next",
        group_next,
        category=CATEGORY,
        description="Show the next object in a group (one at a time)",
        examples=[
            "group_next",
            "group_next my_group",
        ],
        tags=["group", "navigate", "next"],
        see_also=["group_previous", "group_enable", "group_disable"],
    )

    registry.register(
        "group_previous",
        group_previous,
        category=CATEGORY,
        description="Show the previous object in a group (one at a time)",
        examples=[
            "group_previous",
            "group_previous my_group",
        ],
        tags=["group", "navigate", "previous"],
        see_also=["group_next", "group_enable", "group_disable"],
    )

    # ------------------------------------------------------------------- sort
    registry.register(
        "sort_group_objects",
        sort_group_objects,
        category=CATEGORY,
        description="Sort all objects within a group alphabetically",
        examples=[
            "sort_group_objects my_proteins",
            "sort_group_objects structures_group",
        ],
        tags=["group", "sort", "order"],
        see_also=["sort_all_groups", "group_info", "create_sorted_group"],
    )

    registry.register(
        "sort_all_groups",
        sort_all_groups,
        category=CATEGORY,
        description="Sort objects in every PyMOL group alphabetically",
        examples=[
            "sort_all_groups",
        ],
        tags=["group", "sort", "order", "batch"],
        see_also=["sort_group_objects"],
    )

    registry.register(
        "group_info",
        group_info,
        category=CATEGORY,
        description="Display metadata and sorting status for a group",
        examples=[
            "group_info my_proteins",
            "group_info structures_group",
        ],
        tags=["group", "info", "inspect"],
        see_also=["sort_group_objects", "create_sorted_group"],
    )

    registry.register(
        "create_sorted_group",
        create_sorted_group,
        category=CATEGORY,
        description="Create a new group whose members are sorted alphabetically",
        examples=[
            "create_sorted_group my_group",
            "create_sorted_group proteins, proteins_sorted",
        ],
        tags=["group", "sort", "create"],
        see_also=["sort_group_objects", "group_info"],
    )

    # ------------------------------------------------------------------- copy
    registry.register(
        "copy_group",
        copy_group,
        category=CATEGORY,
        description="Copy a group with renamed member objects",
        examples=[
            "copy_group my_structures",
            "copy_group proteins, proteins_backup",
            "copy_group data, data_copy, _backup",
        ],
        tags=["group", "copy", "duplicate"],
        see_also=["copy_group_objects", "list_group_copies"],
    )

    registry.register(
        "copy_group_objects",
        copy_group_objects,
        category=CATEGORY,
        description=(
            "Copy explicitly listed objects into a new group with renamed members"
        ),
        examples=[
            "copy_group_objects obj1,obj2,obj3, my_backup",
            "copy_group_objects protein1,protein2, backup_group, _backup",
        ],
        tags=["group", "copy", "objects"],
        see_also=["copy_group", "list_group_copies"],
    )

    registry.register(
        "list_group_copies",
        list_group_copies,
        category=CATEGORY,
        description="Find all copies of objects belonging to a group",
        examples=[
            "list_group_copies my_structures",
        ],
        tags=["group", "copy", "list"],
        see_also=["copy_group", "copy_group_objects"],
    )

    # ------------------------------------------------------------------ merge
    registry.register(
        "merge_to_group",
        merge_to_group,
        category=CATEGORY,
        description="Merge a structure into every object in a group",
        examples=[
            "merge_to_group my_objects, ligand1",
            "merge_to_group proteins, cofactor, merged_proteins",
        ],
        tags=["group", "merge", "combine"],
        see_also=["merge_to_objects", "list_merged_objects"],
    )

    registry.register(
        "merge_to_objects",
        merge_to_objects,
        category=CATEGORY,
        description="Merge a structure into specific objects",
        examples=[
            "merge_to_objects obj1,obj2,obj3, ligand1",
            "merge_to_objects protein1,protein2, cofactor, merged_proteins",
        ],
        tags=["group", "merge", "combine", "objects"],
        see_also=["merge_to_group", "list_merged_objects"],
    )

    registry.register(
        "list_merged_objects",
        list_merged_objects,
        category=CATEGORY,
        description="List all objects that contain a merged structure",
        examples=[
            "list_merged_objects ligand1",
        ],
        tags=["group", "merge", "list"],
        see_also=["merge_to_group", "merge_to_objects"],
    )

    # --------------------------------------------------------- extract_chain
    registry.register(
        "extract_chain_from_group",
        extract_chain_from_group,
        category=CATEGORY,
        description="Extract a single chain from every object in a group or pattern",
        examples=[
            "extract_chain_from_group my_group, A",
            "extract_chain_from_group protein_*, B, my_prefix",
            "extract_chain_from_group complex, C, chains, 0",
        ],
        tags=["group", "chain", "extract"],
        see_also=["extract_chains_from_group"],
    )

    registry.register(
        "extract_chains_from_group",
        extract_chains_from_group,
        category=CATEGORY,
        description="Extract multiple chains from every object in a group or pattern",
        examples=[
            "extract_chains_from_group my_group, A,B",
            "extract_chains_from_group proteins, A,B,C",
            "extract_chains_from_group complex, A,B, my_prefix, 0",
        ],
        tags=["group", "chain", "extract", "batch"],
        see_also=["extract_chain_from_group"],
    )

    # ------------------------------------------------------- autocompletion
    autocomplete.register("group_enable", 0, completers.group_name, "group")
    autocomplete.register("group_disable", 0, completers.group_name, "group")
    autocomplete.register("group_toggle", 0, completers.group_name, "group")
    autocomplete.register("group_status", 0, completers.group_name, "group")

    autocomplete.register("group_next", 0, completers.group_name, "group")
    autocomplete.register("group_previous", 0, completers.group_name, "group")

    autocomplete.register("sort_group_objects", 0, completers.group_name, "group")
    autocomplete.register("group_info", 0, completers.group_name, "group")
    autocomplete.register(
        "create_sorted_group", 0, completers.group_name, "source_group"
    )

    autocomplete.register("copy_group", 0, completers.group_name, "group")
    autocomplete.register("copy_group_objects", 0, completers.object_name, "object")
    autocomplete.register("list_group_copies", 0, completers.group_name, "group")

    autocomplete.register("merge_to_group", 0, completers.group_name, "group")
    autocomplete.register("merge_to_group", 1, completers.object_name, "struct")
    autocomplete.register("merge_to_objects", 0, completers.object_name, "object")
    autocomplete.register("merge_to_objects", 1, completers.object_name, "struct")
    autocomplete.register("list_merged_objects", 0, completers.object_name, "struct")

    autocomplete.register("extract_chain_from_group", 0, completers.group_name, "group")
    autocomplete.register(
        "extract_chains_from_group", 0, completers.group_name, "group"
    )
