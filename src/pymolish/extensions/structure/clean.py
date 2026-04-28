"""Structure cleanup: remove common ions and metals from PyMOL selections."""

from __future__ import annotations

from pymol import cmd

from ...core.logging import plog

_TAG = "structure.clean"

_IONS = ["NA", "K", "CL", "CA", "MG", "ZN", "MN", "FE", "CU", "CD", "SO4", "PO4"]
_METALS = [
    "ZN",
    "FE",
    "CU",
    "MN",
    "MG",
    "CD",
    "CO",
    "NI",
    "SR",
    "BA",
    "CS",
    "PB",
    "HG",
    "AU",
    "PT",
    "LI",
    "AL",
    "GA",
    "IN",
    "IR",
    "OS",
    "RH",
    "RU",
]


def _clean(value: str) -> str:
    """Strip one layer of surrounding quotes from PyMOL command arguments."""
    if not isinstance(value, str):
        return value
    return value.strip().strip("'\"")


def remove_ions(selection: str = "all") -> int:
    """Remove common small ions from *selection*.

    Deletes atoms matching any of the curated ion residue names within the
    given PyMOL selection: ``NA``, ``K``, ``CL``, ``CA``, ``MG``, ``ZN``,
    ``MN``, ``FE``, ``CU``, ``CD``, ``SO4``, ``PO4``.

    Args:
        selection: PyMOL selection expression (default: ``"all"``).

    Returns:
        Number of residue names removed (i.e. iterations that found matches,
        not total atoms).

    Examples:
        PyMOL> remove_ions
        PyMOL> remove_ions protein_complex
        PyMOL> remove_ions chain A

    Since:
        1.0.0

    See Also:
        remove_metals
    """
    selection = _clean(selection) or "all"
    plog(_TAG, f"removing ions from {selection!r}")
    removed = 0
    for ion in _IONS:
        expr = f"resn {ion} and ({selection})"
        try:
            count = cmd.count_atoms(expr)
            if count > 0:
                cmd.remove(expr)
                removed += 1
        except Exception as exc:  # noqa: BLE001
            plog(_TAG, f"failed to remove {ion}: {exc}", "warn")
    plog(_TAG, f"removed {removed} ion type(s) from {selection!r}")
    return removed


def remove_metals(selection: str = "all") -> int:
    """Remove common metal atoms from *selection*.

    Deletes atoms matching any of the curated metal residue names within the
    given PyMOL selection: ``ZN``, ``FE``, ``CU``, ``MN``, ``MG``, ``CD``,
    ``CO``, ``NI``, ``SR``, ``BA``, ``CS``, ``PB``, ``HG``, ``AU``, ``PT``,
    ``LI``, ``AL``, ``GA``, ``IN``, ``IR``, ``OS``, ``RH``, ``RU``.

    Args:
        selection: PyMOL selection expression (default: ``"all"``).

    Returns:
        Number of residue names removed (i.e. iterations that found matches,
        not total atoms).

    Examples:
        PyMOL> remove_metals
        PyMOL> remove_metals my_protein
        PyMOL> remove_metals chain B

    Since:
        1.0.0

    See Also:
        remove_ions
    """
    selection = _clean(selection) or "all"
    plog(_TAG, f"removing metals from {selection!r}")
    removed = 0
    for metal in _METALS:
        expr = f"resn {metal} and ({selection})"
        try:
            count = cmd.count_atoms(expr)
            if count > 0:
                cmd.remove(expr)
                removed += 1
        except Exception as exc:  # noqa: BLE001
            plog(_TAG, f"failed to remove {metal}: {exc}", "warn")
    plog(_TAG, f"removed {removed} metal type(s) from {selection!r}")
    return removed
