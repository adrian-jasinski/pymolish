# Group "A" menu actions for pymolish group commands

**Status:** finalized (2026-10-22) · **Created:** 2026-10-22 · **Target:** PyMOL Open Source ≥ 3.0
**Tags:** gui, groups, pymol-menu, monkeypatch, sort_group, copy_group, group_enable, group_disable

## Goal

When the user clicks **A** (Action) on a *group* row in the object panel, show four
extra entries wired to registered pymolish commands:

| Menu label | Command executed |
|------------|------------------|
| duplicate  | `copy_group <group>` |
| sort A→Z / sort Z→A | `sort_group <group>, reverse=0|1` (direction flips each click) |
| enable     | `group_enable <group>` |
| disable    | `group_disable <group>` |

Entries must appear **only** for groups, never for molecules, maps, selections or "all".

## Feasibility (verified against pymol-open-source v3.1.0-89-gf1fa2ed4)

Feasible, no PyMOL fork needed. Verified mechanism:

1. `layer3/Executive.cpp:15026-15029` — an A-click on a `cObjectGroup` row calls
   `MenuActivate(..., "group_action", name)`. Molecules go to `"mol_action"`, etc.
   So the group menu has its own entry point.
2. `layer4/Menu.cpp:97` — `PYOBJECT_CALLMETHOD(P_menu, name, "Os", cmd, name)`.
   `P_menu` is the `pymol.menu` *module object* (`layer1/P.cpp:2020`), and the method
   is looked up by attribute **on every click**. Therefore replacing
   `pymol.menu.group_action` from Python takes effect immediately and only for groups.
3. `layer4/PopUp.cpp:241-248` — each item is `[type, label, payload]`:
   `type 2` = header, `type 1` = item, `type 0` = separator. A **string** payload is
   executed with `PParse` (same as typing in the PyMOL console, so registered
   keywords like `sort_group x` work); a **callable** payload is a lazy submenu.
   Leaf actions must be strings, not lambdas.
4. `modules/pymol/menu.py:1217` — current `group_action(self_cmd, sele)` returns a
   plain list; we wrap it and splice our section in.

Constraints: `pymol.menu` is imported by the C++ core at startup (before plugins), so
it always exists in a real PyMOL. In tests / headless mocks it may not, so the patch
must be guarded by `try: from pymol import menu except ImportError`.

## Design (ponytail: one file, one function, no state)

New file `src/pymolish/extensions/groups/_menu.py`:

```python
"""Inject pymolish group commands into PyMOL's group Action (A) menu."""
from __future__ import annotations

from ...core.group_utils import GroupUtils

_SEP = [0, "", ""]


def _sort_entry(group: str) -> list:
    # ponytail: direction derived from current order instead of stored state,
    # so it flips on every real click and never drifts if the menu is cancelled.
    objects = GroupUtils.get_group_objects(group) or []
    ascending = len(objects) > 1 and objects == sorted(objects, key=str.lower)
    reverse = 1 if ascending else 0
    label = "sort Z→A" if ascending else "sort A→Z"
    return [1, label, f"sort_group {group}, reverse={reverse}"]


def pymolish_group_items(group: str) -> list[list]:
    return [
        _SEP,
        [2, "PyMOLish:", ""],
        [1, "duplicate", f"copy_group {group}"],
        _sort_entry(group),
        [1, "enable", f"group_enable {group}"],
        [1, "disable", f"group_disable {group}"],
    ]


def install() -> bool:
    """Wrap ``pymol.menu.group_action``. Idempotent. Returns True when patched."""
    try:
        from pymol import menu
    except ImportError:
        return False
    original = getattr(menu, "group_action", None)
    if original is None or getattr(original, "_pymolish", False):
        return bool(original)

    def group_action(self_cmd, sele):
        items = original(self_cmd, sele)
        # insert after the zoom/orient/center/origin/drag/reset block (index 8)
        return items[:8] + pymolish_group_items(sele) + items[8:]

    group_action._pymolish = True
    group_action._original = original
    menu.group_action = group_action
    return True
```

Hook-up: in `extensions/groups/__init__.py::__init_plugin__`, after registrations:

```python
    from ._menu import install as _install_menu
    _install_menu()
```

Notes
- Insert position index 8 = right after `reset` and its separator in the stock list
  (`menu.py:1218-1226`). If PyMOL ever reorders, worst case our block lands elsewhere;
  no crash.
- Labels: "duplicate", "enable", "disable" as requested; sort label shows the
  direction the click will apply.
- Command strings use PyMOL keyword syntax so they go through the registered
  commands and get logged to the PyMOL log like native menu actions.
- Group names cannot contain spaces in PyMOL, so no quoting is needed.
- No `cmd.extend`, no `print`, no new deps. `plog` only if `install()` fails
  unexpectedly (optional; `ImportError` path is silent by design).

## Steps

1. [x] Create `src/pymolish/extensions/groups/_menu.py` as above.
2. [x] Call `install()` from `extensions/groups/__init__.py::__init_plugin__`.
3. [x] Test `tests/test_groups/test_menu.py`:
   - inject a fake `pymol.menu` module with a stub `group_action` returning 10
     dummy rows; call `install()`; assert the wrapped result contains the four
     labels, that `install()` twice does not double-wrap, and that
     `_sort_entry` yields `reverse=1` for an ascending group and `reverse=0`
     otherwise (mock `GroupUtils.get_group_objects`).
4. [x] Manual check in PyMOL 3.x: `load 1abc; group g, 1abc` → click **A** on `g`
   → entries visible; click **A** on `1abc` → entries absent. Click sort twice →
   order flips.
5. [x] Docs: add a short "Group Action menu" section to `docs/commands/groups.md`
   (no new commands, so no autocompletion changes).
6. [x] Bump patch version in `pyproject.toml` and `src/pymolish/__init__.py`
   (0.1.7 → 0.1.8), `ruff check . && ruff format .`, `pytest tests/`, commit.
7. [x] Move this file to `plans/finalized/`.

## Expected outputs

- `src/pymolish/extensions/groups/_menu.py` (~45 lines)
- 2-line change in `extensions/groups/__init__.py`
- `tests/test_groups/test_menu.py`
- `docs/commands/groups.md` section
- Version 0.1.8

## Risks / open points

- Relies on a private module (`pymol.menu`) with no API guarantee. Signature
  `group_action(self_cmd, sele)` is unchanged from 2.x through 3.2.0a; cheap to
  re-verify on upgrades.
- Other plugins patching `group_action` are chained, not clobbered (we wrap
  whatever is there at install time).
- Skipped: a Qt context-menu variant and a user-configurable item list. Add only if
  someone asks.

## Update 2026-10-27 (v0.1.13)

Entries moved next to PyMOL's own `rename group` / `group` / `delete group` rows
(inserted right after `delete group`, found by label; fallback row 8). Labels are
blue (`\359` escape, same mechanism as the stock red `\933delete group`) and read
`duplicate group`, `sort group`, `enable group`, `disable group`. The separate
"PyMOLish:" header and separator were dropped.
