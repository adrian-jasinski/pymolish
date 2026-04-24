"""Copy PyMOL groups and objects with renamed members."""

from __future__ import annotations

from pymol import cmd

from pymolish.core.group_utils import GroupUtils
from pymolish.core.logging import plog

_TAG = "groups.copy"


def _clean(value: str) -> str:
    """Strip one layer of surrounding quotes from a PyMOL command argument."""
    if not isinstance(value, str):
        return value
    return value.strip().strip("'\"")


def copy_group(
    group_name: str,
    new_group_name: str = "",
    object_suffix: str = "_cpy",
) -> list[str]:
    """Copy a group, renaming each member object with *object_suffix*.

    Args:
        group_name: Name of the source group.
        new_group_name: Name for the new group.  Defaults to
            ``<group_name>_cpy``.
        object_suffix: Suffix appended to each copied object name (default
            ``"_cpy"``).

    Returns:
        List of successfully copied object names in the new group.

    Examples:
        PyMOL> copy_group my_structures
        PyMOL> copy_group proteins, proteins_backup
        PyMOL> copy_group data, data_copy, _backup

    Since:
        1.0.0

    See Also:
        copy_group_objects, list_group_copies
    """
    group_name = _clean(group_name)
    new_group_name = _clean(new_group_name) or f"{group_name}_cpy"
    object_suffix = _clean(object_suffix)

    objects = GroupUtils.get_group_objects(group_name)
    if not objects:
        plog(_TAG, f"group {group_name!r} not found or empty", "error")
        return []

    plog(
        _TAG,
        f"copying {len(objects)} object(s) from {group_name!r} -> {new_group_name!r}",
    )

    copied: list[str] = []
    failed: list[str] = []

    for obj in objects:
        new_obj = f"{obj}{object_suffix}"
        if GroupUtils.is_object(new_obj):
            plog(_TAG, f"object {new_obj!r} already exists; skipping", "warn")
            failed.append(obj)
            continue
        try:
            cmd.copy(new_obj, obj)
            copied.append(new_obj)
            plog(_TAG, f"  {obj!r} -> {new_obj!r}")
        except Exception as exc:  # noqa: BLE001
            plog(_TAG, f"failed to copy {obj!r}: {exc}", "error")
            failed.append(obj)

    if copied:
        try:
            GroupUtils.ensure_group(new_group_name, copied)
        except Exception as exc:  # noqa: BLE001
            plog(_TAG, f"failed to create group {new_group_name!r}: {exc}", "error")

    plog(
        _TAG,
        f"copied {len(copied)}/{len(objects)} object(s); "
        f"{len(failed)} failed; group={new_group_name!r}",
    )
    return copied


def copy_group_objects(
    object_names: str,
    new_group_name: str,
    object_suffix: str = "_cpy",
) -> list[str]:
    """Copy explicitly listed objects into a new group with renamed members.

    Args:
        object_names: Comma-separated object names.
        new_group_name: Name of the destination group (created if absent).
        object_suffix: Suffix appended to each copied object name (default
            ``"_cpy"``).

    Returns:
        List of successfully copied object names.

    Examples:
        PyMOL> copy_group_objects obj1,obj2,obj3, my_backup
        PyMOL> copy_group_objects protein1,protein2, backup_group, _backup

    Since:
        1.0.0

    See Also:
        copy_group, list_group_copies
    """
    new_group_name = _clean(new_group_name)
    object_suffix = _clean(object_suffix)

    raw_names = [_clean(n) for n in str(object_names).split(",") if _clean(n)]
    if not raw_names:
        plog(_TAG, "object_names must be non-empty", "error")
        return []

    valid = [n for n in raw_names if GroupUtils.is_object(n)]
    missing = [n for n in raw_names if n not in valid]
    for m in missing:
        plog(_TAG, f"object {m!r} not found; skipping", "warn")

    if not valid:
        plog(_TAG, "no valid objects found", "error")
        return []

    plog(_TAG, f"copying {len(valid)} object(s) into {new_group_name!r}")

    copied: list[str] = []
    for obj in valid:
        new_obj = f"{obj}{object_suffix}"
        if GroupUtils.is_object(new_obj):
            plog(_TAG, f"object {new_obj!r} already exists; skipping", "warn")
            continue
        try:
            cmd.copy(new_obj, obj)
            copied.append(new_obj)
            plog(_TAG, f"  {obj!r} -> {new_obj!r}")
        except Exception as exc:  # noqa: BLE001
            plog(_TAG, f"failed to copy {obj!r}: {exc}", "error")

    if copied:
        try:
            GroupUtils.ensure_group(new_group_name, copied)
        except Exception as exc:  # noqa: BLE001
            plog(_TAG, f"failed to create group {new_group_name!r}: {exc}", "error")

    plog(_TAG, f"copied {len(copied)}/{len(valid)} object(s) into {new_group_name!r}")
    return copied


def list_group_copies(group_name: str) -> dict[str, list[str]]:
    """Find objects whose names start with any member of *group_name*.

    This heuristic detects copies created by :func:`copy_group`.

    Args:
        group_name: Name of the original source group.

    Returns:
        Dict mapping each original member name to the list of copies found.
        Only members that have at least one copy are included.

    Examples:
        PyMOL> list_group_copies my_structures

    Since:
        1.0.0

    See Also:
        copy_group, copy_group_objects
    """
    group_name = _clean(group_name)

    original_objects = GroupUtils.get_group_objects(group_name)
    if not original_objects:
        plog(_TAG, f"group {group_name!r} not found or empty", "warn")
        return {}

    all_objects = GroupUtils.get_all_objects()
    copies: dict[str, list[str]] = {}

    for orig in original_objects:
        found = [o for o in all_objects if o.startswith(orig) and o != orig]
        if found:
            copies[orig] = sorted(found)

    if copies:
        plog(_TAG, f"found copies for {len(copies)}/{len(original_objects)} member(s)")
        for orig, found in copies.items():
            plog(_TAG, f"  {orig!r}: {', '.join(found)}")
    else:
        plog(_TAG, f"no copies found for group {group_name!r}")

    return copies
