"""Navigate group objects: show next or previous object one at a time."""

from __future__ import annotations

from pymol import cmd

from ...core.group_utils import GroupUtils
from ...core.logging import plog

_TAG = "groups.navigate"


def _clean(value: str) -> str:
    """Strip one layer of surrounding quotes from a PyMOL command argument."""
    if not isinstance(value, str):
        return value
    return value.strip().strip("'\"")


def _get_group_members(group_name: str) -> list[str]:
    """Return group members in stable order.

    Prefers ``cmd.get_object_list('(group)')`` for GUI-like ordering, then
    falls back to :meth:`GroupUtils.get_group_objects`.
    """
    try:
        members = cmd.get_object_list(f"({group_name})")
        if members:
            return list(members)
    except Exception:  # noqa: BLE001
        pass
    result = GroupUtils.get_group_objects(group_name)
    return list(result) if result else []


def _resolve_group(group_name: str) -> str | None:
    """Return the group to navigate, or ``None`` with a logged message.

    When *group_name* is provided it is validated directly.  When omitted the
    function tries to infer the unique active group from the scene.
    """
    if group_name:
        members = _get_group_members(group_name)
        if not members:
            plog(_TAG, f"group {group_name!r} not found or empty", "warn")
            return None
        return group_name

    groups = GroupUtils.get_all_groups()
    if not groups:
        plog(_TAG, "no groups found; specify group e.g. group_next my_group", "warn")
        return None

    # Prefer the single enabled group.
    enabled_groups: list[str] = []
    try:
        enabled_groups = list(cmd.get_names("group_objects", enabled_only=1) or [])
    except Exception:  # noqa: BLE001
        pass
    if len(enabled_groups) == 1 and _get_group_members(enabled_groups[0]):
        return enabled_groups[0]

    # Infer from enabled members.
    try:
        enabled = set(cmd.get_names("objects", enabled_only=1) or [])
    except Exception:  # noqa: BLE001
        enabled = set()

    with_enabled = [
        g for g in groups if any(m in enabled for m in _get_group_members(g))
    ]
    if len(with_enabled) == 1:
        return with_enabled[0]
    if len(with_enabled) > 1:
        candidates = ", ".join(sorted(with_enabled))
        plog(_TAG, f"multiple active groups ({candidates}); specify one", "warn")
        return None

    if len(groups) == 1:
        return groups[0]

    example = sorted(groups)[0]
    plog(_TAG, f"multiple groups exist; specify one e.g. group_next {example}", "warn")
    return None


def _navigate(group_name: str, direction: int) -> str | None:
    """Shared logic for next (direction=+1) / previous (direction=-1).

    Returns the name of the newly shown object, or ``None`` on failure.
    """
    members = _get_group_members(group_name)
    if not members:
        return None

    try:
        enabled_objects = set(cmd.get_names("objects", enabled_only=1) or [])
    except Exception:  # noqa: BLE001
        enabled_objects = set()

    enabled_in_group = [obj for obj in members if obj in enabled_objects]
    n = len(members)

    if len(enabled_in_group) > 1:
        plog(
            _TAG,
            f"multiple objects enabled in {group_name!r}; "
            "run group_disable first to view one at a time",
            "warn",
        )
        return None

    if not enabled_in_group:
        # No selection: forward → first, backward → last.
        idx = 0 if direction == 1 else n - 1
    else:
        current_idx = members.index(enabled_in_group[0])
        old_idx = current_idx
        idx = (current_idx + direction) % n
        try:
            cmd.enable(members[idx], parents=1)
            cmd.disable(members[old_idx])
            plog(_TAG, f"viewing: {members[idx]}")
            return members[idx]
        except Exception as exc:  # noqa: BLE001
            plog(_TAG, f"navigation error: {exc}", "error")
            return None

    try:
        cmd.enable(members[idx], parents=1)
        plog(_TAG, f"viewing: {members[idx]}")
        return members[idx]
    except Exception as exc:  # noqa: BLE001
        plog(_TAG, f"navigation error: {exc}", "error")
        return None


def group_next(group_name: str = "") -> str | None:
    """Show the next object in a group (one at a time).

    Disables the current object and enables the next one (wrapping around).
    When no object is enabled, enables the first.  When more than one object
    is enabled, asks the user to run ``group_disable`` first.

    Args:
        group_name: Group to navigate.  When omitted, the function infers
            the active group from the scene (works best with a single group).

    Returns:
        Name of the newly shown object, or ``None`` if navigation was not
        possible.

    Examples:
        PyMOL> group_next
        PyMOL> group_next my_group

    Since:
        1.0.0

    See Also:
        group_previous, group_enable, group_disable
    """
    group_name = _clean(group_name)
    resolved = _resolve_group(group_name)
    if resolved is None:
        return None
    return _navigate(resolved, 1)


def group_previous(group_name: str = "") -> str | None:
    """Show the previous object in a group (one at a time).

    Same resolution rules as :func:`group_next` but moves in the reverse
    direction.  When no object is enabled, enables the last.

    Args:
        group_name: Group to navigate.  When omitted, the active group is
            inferred from the scene.

    Returns:
        Name of the newly shown object, or ``None`` if navigation was not
        possible.

    Examples:
        PyMOL> group_previous
        PyMOL> group_previous my_group

    Since:
        1.0.0

    See Also:
        group_next, group_enable, group_disable
    """
    group_name = _clean(group_name)
    resolved = _resolve_group(group_name)
    if resolved is None:
        return None
    return _navigate(resolved, -1)
