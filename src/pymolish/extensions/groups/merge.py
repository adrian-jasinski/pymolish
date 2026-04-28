"""Merge a structure into every object in a group."""

from __future__ import annotations

from pymol import cmd

from ...core.group_utils import GroupUtils
from ...core.logging import plog

_TAG = "groups.merge"


def _clean(value: str) -> str:
    """Strip one layer of surrounding quotes from a PyMOL command argument."""
    if not isinstance(value, str):
        return value
    return value.strip().strip("'\"")


def merge_to_group(
    group_name: str,
    struct_name: str,
    new_group_name: str = "",
) -> list[str]:
    """Merge *struct_name* into every object in *group_name*.

    For each member object ``obj``, creates ``<obj>_with_<struct_name>`` by
    unioning the two selections, then collects the new objects into
    *new_group_name*.

    Args:
        group_name: Name of the group whose members are the merge targets.
        struct_name: Name of the structure to merge into each target.
        new_group_name: Name for the result group.  Defaults to
            ``merge_to_<struct_name>``.

    Returns:
        List of successfully created merged object names.

    Examples:
        PyMOL> merge_to_group my_objects, ligand1
        PyMOL> merge_to_group proteins, cofactor, merged_proteins

    Since:
        1.0.0

    See Also:
        merge_to_objects, list_merged_objects
    """
    group_name = _clean(group_name)
    struct_name = _clean(struct_name)
    new_group_name = _clean(new_group_name) or f"merge_to_{struct_name}"

    if not GroupUtils.is_object(struct_name):
        plog(_TAG, f"structure {struct_name!r} not found", "error")
        return []

    objects = GroupUtils.get_group_objects(group_name)
    if not objects:
        plog(_TAG, f"group {group_name!r} not found or empty", "error")
        return []

    plog(
        _TAG,
        f"merging {struct_name!r} into {len(objects)} object(s) from {group_name!r}",
    )

    merged: list[str] = []
    failed: list[str] = []

    for obj in objects:
        new_obj = f"{obj}_with_{struct_name}"
        if GroupUtils.is_object(new_obj):
            plog(_TAG, f"object {new_obj!r} already exists; skipping", "warn")
            failed.append(obj)
            continue

        sel_name = f"_pymolish_merge_{obj}"
        try:
            cmd.select(sel_name, f"{obj} or {struct_name}")
            cmd.create(new_obj, sel_name)
            cmd.delete(sel_name)
            merged.append(new_obj)
            plog(_TAG, f"  {obj!r} + {struct_name!r} -> {new_obj!r}")
        except Exception as exc:  # noqa: BLE001
            plog(_TAG, f"failed to merge {obj!r}: {exc}", "error")
            try:
                cmd.delete(sel_name)
            except Exception:  # noqa: BLE001
                pass
            failed.append(obj)

    if merged:
        try:
            GroupUtils.ensure_group(new_group_name, merged)
        except Exception as exc:  # noqa: BLE001
            plog(_TAG, f"failed to create group {new_group_name!r}: {exc}", "error")

    plog(
        _TAG,
        f"merged {len(merged)}/{len(objects)} object(s); "
        f"{len(failed)} failed; group={new_group_name!r}",
    )
    return merged


def merge_to_objects(
    object_names: str,
    struct_name: str,
    new_group_name: str = "",
) -> list[str]:
    """Merge *struct_name* into a specific set of objects.

    Args:
        object_names: Comma-separated object names to use as merge targets.
        struct_name: Name of the structure to merge into each target.
        new_group_name: Name for the result group.  Defaults to
            ``merge_to_<struct_name>``.

    Returns:
        List of successfully created merged object names.

    Examples:
        PyMOL> merge_to_objects obj1,obj2,obj3, ligand1
        PyMOL> merge_to_objects protein1,protein2, cofactor, merged_proteins

    Since:
        1.0.0

    See Also:
        merge_to_group, list_merged_objects
    """
    struct_name = _clean(struct_name)
    new_group_name = _clean(new_group_name) or f"merge_to_{struct_name}"

    if not GroupUtils.is_object(struct_name):
        plog(_TAG, f"structure {struct_name!r} not found", "error")
        return []

    raw_names = [_clean(n) for n in str(object_names).split(",") if _clean(n)]
    if not raw_names:
        plog(_TAG, "object_names must be non-empty", "error")
        return []

    valid = [n for n in raw_names if GroupUtils.is_object(n)]
    for m in [n for n in raw_names if n not in valid]:
        plog(_TAG, f"object {m!r} not found; skipping", "warn")

    if not valid:
        plog(_TAG, "no valid objects found", "error")
        return []

    plog(_TAG, f"merging {struct_name!r} into {len(valid)} object(s)")

    merged: list[str] = []
    for obj in valid:
        new_obj = f"{obj}_with_{struct_name}"
        if GroupUtils.is_object(new_obj):
            plog(_TAG, f"object {new_obj!r} already exists; skipping", "warn")
            continue

        sel_name = f"_pymolish_merge_{obj}"
        try:
            cmd.select(sel_name, f"{obj} or {struct_name}")
            cmd.create(new_obj, sel_name)
            cmd.delete(sel_name)
            merged.append(new_obj)
            plog(_TAG, f"  {obj!r} + {struct_name!r} -> {new_obj!r}")
        except Exception as exc:  # noqa: BLE001
            plog(_TAG, f"failed to merge {obj!r}: {exc}", "error")
            try:
                cmd.delete(sel_name)
            except Exception:  # noqa: BLE001
                pass

    if merged:
        try:
            GroupUtils.ensure_group(new_group_name, merged)
        except Exception as exc:  # noqa: BLE001
            plog(_TAG, f"failed to create group {new_group_name!r}: {exc}", "error")

    plog(_TAG, f"merged {len(merged)}/{len(valid)} object(s) into {new_group_name!r}")
    return merged


def list_merged_objects(struct_name: str) -> list[str]:
    """Find all objects whose names contain ``_with_<struct_name>``.

    Args:
        struct_name: Structure name to search for in object names.

    Returns:
        Sorted list of matching object names.

    Examples:
        PyMOL> list_merged_objects ligand1

    Since:
        1.0.0

    See Also:
        merge_to_group, merge_to_objects
    """
    struct_name = _clean(struct_name)
    if not struct_name:
        plog(_TAG, "struct_name must be non-empty", "error")
        return []

    suffix = f"_with_{struct_name}"
    all_objects = GroupUtils.get_all_objects()
    found = sorted(o for o in all_objects if suffix in o)

    if found:
        plog(_TAG, f"found {len(found)} merged object(s) for {struct_name!r}")
        for obj in found:
            plog(_TAG, f"  {obj}")
    else:
        plog(_TAG, f"no merged objects found for {struct_name!r}")

    return found
