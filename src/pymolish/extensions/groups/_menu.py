"""Inject pymolish group commands into PyMOL's group Action (``A``) menu.

PyMOL builds the object-panel popup by calling ``pymol.menu.group_action``
on every click (looked up by attribute on the module), so wrapping that one
function adds entries for groups only — molecules, maps and selections use
other entry points.  Leaf items must be command strings; PyMOL runs them
through its parser exactly like console input.
"""

from __future__ import annotations

from collections.abc import Callable

from ...core.group_utils import GroupUtils

_SEP: list = [0, "", ""]


def _sort_entry(group: str) -> list:
    # ponytail: direction derived from the current order instead of stored state,
    # so it flips on every real click and never drifts if the menu is cancelled.
    objects = GroupUtils.get_group_objects(group) or []
    ascending = len(objects) > 1 and objects == sorted(objects, key=str.lower)
    reverse = 1 if ascending else 0
    # PyMOL popup menus render ASCII only, so no arrows in the label.
    return [1, "sort", f"sort_group {group}, reverse={reverse}"]


def pymolish_group_items(group: str) -> list[list]:
    """Return the menu rows appended to the group Action menu."""
    return [
        _SEP,
        [2, "PyMOLish:", ""],
        [1, "duplicate", f"copy_group {group}"],
        _sort_entry(group),
        [1, "enable", f"group_enable {group}"],
        [1, "disable", f"group_disable {group}"],
    ]


# Rows 0-7 of the stock menu are the zoom/orient/center/origin/drag/reset block.
_INSERT_AT = 8


def install() -> bool:
    """Wrap ``pymol.menu.group_action``.  Idempotent.  Returns True when active."""
    try:
        from pymol import menu
    except ImportError:
        return False
    original: Callable | None = getattr(menu, "group_action", None)
    if original is None:
        return False
    if getattr(original, "_pymolish", False):
        return True

    def group_action(self_cmd: object, sele: str) -> list:
        items = list(original(self_cmd, sele))
        return items[:_INSERT_AT] + pymolish_group_items(sele) + items[_INSERT_AT:]

    group_action._pymolish = True  # type: ignore[attr-defined]
    group_action._original = original  # type: ignore[attr-defined]
    menu.group_action = group_action
    return True
