"""Enable, disable, toggle, and report visibility of group objects."""

from __future__ import annotations

from pymol import cmd

from ...core.group_utils import GroupUtils
from ...core.logging import plog

_TAG = "groups.toggle"


def _clean(value: str) -> str:
    """Strip one layer of surrounding quotes from a PyMOL command argument."""
    if not isinstance(value, str):
        return value
    return value.strip().strip("'\"")


def _resolve_targets(group_pattern: str) -> list[str]:
    """Return the sorted list of target objects for *group_pattern*.

    Resolution order: group members → exact object → pattern match.
    Returns an empty list when nothing matches.
    """
    if GroupUtils.is_group(group_pattern):
        objs = GroupUtils.get_group_objects(group_pattern) or []
        if objs:
            return sorted(objs)

    if GroupUtils.is_object(group_pattern):
        return [group_pattern]

    matches = GroupUtils.find_objects_by_pattern(group_pattern)
    return sorted(matches)


def group_enable(group_pattern: str, each: int | str = 1) -> list[str]:
    """Enable objects resolved from *group_pattern*.

    Args:
        group_pattern: Group name, object name, or wildcard pattern.
        each: Enable every *nth* object (``1`` = all, ``2`` = every second, …).

    Returns:
        Names of objects that were successfully enabled.

    Examples:
        PyMOL> group_enable my_group
        PyMOL> group_enable my_group, 2
        PyMOL> group_enable chain_*

    Since:
        1.0.0

    See Also:
        group_disable, group_toggle, group_status
    """
    group_pattern = _clean(group_pattern)
    each = int(each)

    targets = _resolve_targets(group_pattern)
    if not targets:
        plog(_TAG, f"no objects match {group_pattern!r}", "warn")
        return []

    selected = targets[::each] if each > 1 else targets

    enabled: list[str] = []
    for obj in selected:
        try:
            cmd.enable(obj)
            enabled.append(obj)
        except Exception as exc:  # noqa: BLE001
            plog(_TAG, f"failed to enable {obj!r}: {exc}", "error")

    plog(
        _TAG,
        f"enabled {len(enabled)}/{len(selected)} object(s) from {group_pattern!r}",
    )
    return enabled


def group_disable(group_pattern: str, each: int | str = 1) -> list[str]:
    """Disable objects resolved from *group_pattern*.

    Args:
        group_pattern: Group name, object name, or wildcard pattern.
        each: Disable every *nth* object (``1`` = all, ``2`` = every second, …).

    Returns:
        Names of objects that were successfully disabled.

    Examples:
        PyMOL> group_disable my_group
        PyMOL> group_disable my_group, 2
        PyMOL> group_disable chain_*

    Since:
        1.0.0

    See Also:
        group_enable, group_toggle, group_status
    """
    group_pattern = _clean(group_pattern)
    each = int(each)

    targets = _resolve_targets(group_pattern)
    if not targets:
        plog(_TAG, f"no objects match {group_pattern!r}", "warn")
        return []

    selected = targets[::each] if each > 1 else targets

    disabled: list[str] = []
    for obj in selected:
        try:
            cmd.disable(obj)
            disabled.append(obj)
        except Exception as exc:  # noqa: BLE001
            plog(_TAG, f"failed to disable {obj!r}: {exc}", "error")

    plog(
        _TAG,
        f"disabled {len(disabled)}/{len(selected)} object(s) from {group_pattern!r}",
    )
    return disabled


def group_toggle(group_pattern: str, each: int | str = 1) -> dict[str, list[str]]:
    """Toggle visibility of objects resolved from *group_pattern*.

    Objects that are currently enabled are disabled and vice versa.

    Args:
        group_pattern: Group name, object name, or wildcard pattern.
        each: Toggle every *nth* object (``1`` = all, ``2`` = every second, …).

    Returns:
        Dict with keys ``"enabled"`` and ``"disabled"`` listing the objects
        that were transitioned into each state.

    Examples:
        PyMOL> group_toggle my_group
        PyMOL> group_toggle my_group, 2

    Since:
        1.0.0

    See Also:
        group_enable, group_disable, group_status
    """
    group_pattern = _clean(group_pattern)
    each = int(each)

    targets = _resolve_targets(group_pattern)
    if not targets:
        plog(_TAG, f"no objects match {group_pattern!r}", "warn")
        return {"enabled": [], "disabled": []}

    selected = targets[::each] if each > 1 else targets

    toggled_on: list[str] = []
    toggled_off: list[str] = []

    for obj in selected:
        try:
            if cmd.get_setting_int("enabled", obj):
                cmd.disable(obj)
                toggled_off.append(obj)
            else:
                cmd.enable(obj)
                toggled_on.append(obj)
        except Exception as exc:  # noqa: BLE001
            plog(_TAG, f"failed to toggle {obj!r}: {exc}", "error")

    plog(
        _TAG,
        f"toggled {len(selected)} object(s): {len(toggled_on)} enabled, "
        f"{len(toggled_off)} disabled",
    )
    return {"enabled": toggled_on, "disabled": toggled_off}


def group_status(group_pattern: str) -> dict[str, list[str]]:
    """Report the enabled/disabled state of objects matching *group_pattern*.

    Args:
        group_pattern: Group name, object name, or wildcard pattern.

    Returns:
        Dict with keys ``"enabled"`` and ``"disabled"`` listing matched objects
        in each state.  Both lists are empty when nothing matches.

    Examples:
        PyMOL> group_status my_group
        PyMOL> group_status chain_*

    Since:
        1.0.0

    See Also:
        group_enable, group_disable, group_toggle
    """
    group_pattern = _clean(group_pattern)

    targets = _resolve_targets(group_pattern)
    if not targets:
        plog(_TAG, f"no objects match {group_pattern!r}", "warn")
        return {"enabled": [], "disabled": []}

    enabled: list[str] = []
    disabled: list[str] = []

    for obj in targets:
        try:
            if cmd.get_setting_int("enabled", obj):
                enabled.append(obj)
            else:
                disabled.append(obj)
        except Exception as exc:  # noqa: BLE001
            plog(_TAG, f"error checking status of {obj!r}: {exc}", "error")

    plog(
        _TAG,
        f"{len(targets)} object(s): {len(enabled)} enabled, {len(disabled)} disabled",
    )
    return {"enabled": enabled, "disabled": disabled}
