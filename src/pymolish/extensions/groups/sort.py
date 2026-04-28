"""Sort objects within PyMOL groups by name."""

from __future__ import annotations

from ...core.group_utils import GroupUtils
from ...core.logging import plog

_TAG = "groups.sort"


def _clean(value: str) -> str:
    """Strip one layer of surrounding quotes from a PyMOL command argument."""
    if not isinstance(value, str):
        return value
    return value.strip().strip("'\"")


def sort_group_objects(group_name: str) -> list[str]:
    """Sort all objects within a group alphabetically (case-insensitive).

    Removes objects from the group one-by-one then re-adds them in sorted
    order.  Object data is not modified — only the group membership order
    changes.

    Args:
        group_name: Name of an existing PyMOL group.

    Returns:
        The sorted list of object names, or an empty list when the group does
        not exist or contains fewer than two objects.

    Examples:
        PyMOL> sort_group_objects my_proteins
        PyMOL> sort_group_objects structures_group

    Since:
        1.0.0

    See Also:
        sort_all_groups, group_info, create_sorted_group
    """
    group_name = _clean(group_name)

    objects = GroupUtils.get_group_objects(group_name)
    if objects is None:
        plog(_TAG, f"group {group_name!r} not found", "error")
        return []
    if not objects:
        plog(_TAG, f"group {group_name!r} is empty", "warn")
        return []
    if len(objects) <= 1:
        plog(
            _TAG,
            f"group {group_name!r} has only {len(objects)} object(s); nothing to sort",
        )
        return list(objects)

    sorted_objects = sorted(objects, key=str.lower)
    if objects == sorted_objects:
        plog(_TAG, f"group {group_name!r} is already sorted")
        return sorted_objects

    # Remove then re-add in sorted order.
    try:
        for obj in objects:
            GroupUtils.remove_from_group(group_name, obj)
        for obj in sorted_objects:
            GroupUtils.add_to_group(group_name, obj)
    except Exception as exc:  # noqa: BLE001
        plog(_TAG, f"failed to reorder {group_name!r}: {exc}", "error")
        # Attempt to restore original order.
        try:
            for obj in objects:
                GroupUtils.remove_from_group(group_name, obj)
            for obj in objects:
                GroupUtils.add_to_group(group_name, obj)
            plog(_TAG, "original order restored", "warn")
        except Exception:  # noqa: BLE001
            plog(
                _TAG,
                "could not restore original order — manual fix may be required",
                "error",
            )
        return []

    plog(_TAG, f"sorted {len(sorted_objects)} object(s) in {group_name!r}")
    return sorted_objects


def sort_all_groups() -> dict[str, list[str]]:
    """Sort objects in every PyMOL group alphabetically.

    Returns:
        Dict mapping group name to the sorted object list for that group.
        Groups that failed or were skipped are not included.

    Examples:
        PyMOL> sort_all_groups

    Since:
        1.0.0

    See Also:
        sort_group_objects
    """
    groups = GroupUtils.get_all_groups()
    if not groups:
        plog(_TAG, "no groups found")
        return {}

    results: dict[str, list[str]] = {}
    for grp in groups:
        sorted_objs = sort_group_objects(grp)
        if sorted_objs:
            results[grp] = sorted_objs

    plog(_TAG, f"sorted {len(results)}/{len(groups)} group(s)")
    return results


def group_info(group_name: str) -> dict[str, object]:
    """Return metadata about a PyMOL group.

    Args:
        group_name: Name of an existing PyMOL group.

    Returns:
        Dict with keys ``"name"``, ``"object_count"``, ``"objects"``, and
        ``"is_sorted"``.  An empty dict is returned when the group is not found.

    Examples:
        PyMOL> group_info my_proteins
        PyMOL> group_info structures_group

    Since:
        1.0.0

    See Also:
        sort_group_objects, create_sorted_group
    """
    group_name = _clean(group_name)

    objects = GroupUtils.get_group_objects(group_name)
    if objects is None:
        plog(_TAG, f"group {group_name!r} not found", "error")
        return {}

    sorted_objects = sorted(objects, key=str.lower)
    is_sorted = objects == sorted_objects

    info: dict[str, object] = {
        "name": group_name,
        "object_count": len(objects),
        "objects": list(objects),
        "is_sorted": is_sorted,
    }

    plog(_TAG, f"group={group_name!r} objects={len(objects)} sorted={is_sorted}")
    for i, obj in enumerate(objects, 1):
        plog(_TAG, f"  {i:>3}. {obj}")

    return info


def create_sorted_group(source_group: str, new_group_name: str = "") -> list[str]:
    """Create a new group whose members are the sorted objects from *source_group*.

    The source group is left untouched.

    Args:
        source_group: Name of an existing group to copy from.
        new_group_name: Name for the new sorted group.  Defaults to
            ``<source_group>_sorted``.

    Returns:
        Sorted list of object names added to the new group, or an empty list
        on failure.

    Examples:
        PyMOL> create_sorted_group my_group
        PyMOL> create_sorted_group proteins, proteins_sorted

    Since:
        1.0.0

    See Also:
        sort_group_objects, group_info
    """
    source_group = _clean(source_group)
    new_group_name = _clean(new_group_name) or f"{source_group}_sorted"

    source_objects = GroupUtils.get_group_objects(source_group)
    if source_objects is None:
        plog(_TAG, f"source group {source_group!r} not found", "error")
        return []
    if not source_objects:
        plog(_TAG, f"source group {source_group!r} is empty", "warn")
        return []

    sorted_objects = sorted(source_objects, key=str.lower)

    try:
        GroupUtils.ensure_group(new_group_name, sorted_objects)
    except Exception as exc:  # noqa: BLE001
        plog(_TAG, f"failed to create group {new_group_name!r}: {exc}", "error")
        return []

    n = len(sorted_objects)
    plog(_TAG, f"created {new_group_name!r} with {n} sorted object(s)")
    return sorted_objects
