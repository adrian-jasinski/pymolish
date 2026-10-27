"""Quick selections for water and common ions, with show/hide toggles."""

from __future__ import annotations

from pymol import cmd

from ...core.cli import clean as _clean
from ...core.logging import plog

_TAG = "selection.solvent"

# ponytail: common PDB ion residue names; extend the tuple if one is missing
_ION_RESNAMES = (
    "NA", "K", "CL", "MG", "CA", "ZN", "MN", "FE", "FE2", "CU", "CU1",
    "CO", "NI", "CD", "HG", "BR", "IOD", "F", "LI", "RB", "CS", "SR",
    "BA", "AL", "PB", "PT", "AU", "AG", "SO4", "PO4", "NO3", "ACT", "FMT",
)  # fmt: skip

WATER_SELECTION = "solvent"
ION_SELECTION = "resn " + "+".join(_ION_RESNAMES)


def _next_name(base: str) -> str:
    """Return ``base`` or the first free ``base<N>`` among existing names."""
    existing = set(cmd.get_names("all") or [])
    if base not in existing:
        return base
    n = 1
    while f"{base}{n}" in existing:
        n += 1
    return f"{base}{n}"


def _solvent_cmd(base: str, expr: str, mode: str) -> str:
    mode = _clean(mode).lower()
    if mode == "on":
        cmd.show("lines", expr)
        plog(_TAG, f"show lines, {expr}")
        return ""
    if mode == "off":
        cmd.hide("everything", expr)
        plog(_TAG, f"hide everything, {expr}")
        return ""
    if mode:
        plog(_TAG, f"unknown mode {mode!r}; use 'on' or 'off'", "error")
        return ""
    name = _next_name(base)
    cmd.select(name, expr)
    plog(_TAG, f"select {name}, {expr}")
    return name


def water(mode: str = "") -> str:
    """Select water molecules, or show/hide them.

    With no argument creates a selection named ``water`` (or ``water1``,
    ``water2``, ... if the name is taken) from ``solvent``.

    Args:
        mode: ``""`` to create a selection, ``"on"`` to ``show lines, solvent``,
            ``"off"`` to ``hide everything, solvent``.

    Returns:
        Name of the created selection, or ``""`` for on/off modes.

    Examples:
        PyMOL> water
        PyMOL> water on
        PyMOL> water off

    Since:
        0.1.12

    See Also:
        ions
    """
    return _solvent_cmd("water", WATER_SELECTION, mode)


def ions(mode: str = "") -> str:
    """Select common ions (NA, CL, MG, CA, ZN, ...), or show/hide them.

    With no argument creates a selection named ``ions`` (or ``ions1``,
    ``ions2``, ... if the name is taken) matching popular ion residue names.

    Args:
        mode: ``""`` to create a selection, ``"on"`` to show ions as lines,
            ``"off"`` to hide them.

    Returns:
        Name of the created selection, or ``""`` for on/off modes.

    Examples:
        PyMOL> ions
        PyMOL> ions on
        PyMOL> ions off

    Since:
        0.1.12

    See Also:
        water
    """
    return _solvent_cmd("ions", ION_SELECTION, mode)
