"""Export residues of a PyMOL selection to a CSV file."""

from __future__ import annotations

import csv
from pathlib import Path

from pymol import cmd

from ...core.logging import plog

_TAG = "io.byres"


def _clean(value: str) -> str:
    """Strip one layer of surrounding quotes from PyMOL command arguments."""
    if not isinstance(value, str):
        return value
    return value.strip().strip("'\"")


def export_byres_to_csv(selection: str, outfile: str) -> int:
    """Write every residue in ``selection`` to ``outfile`` as CSV.

    Output columns: ``chain,resname,resid``. Duplicates are dropped and the
    rows are sorted deterministically.

    Args:
        selection: PyMOL selection expression (e.g. ``"protein"``, ``"chain A"``).
        outfile: Destination CSV path. Parent directories are created if needed.

    Returns:
        Number of unique residues written (``0`` on empty or failed selection).

    Examples:
        PyMOL> export_byres_to_csv protein, residues.csv
        PyMOL> export_byres_to_csv chain A, ./out/chain_a.csv
        PyMOL> export_byres_to_csv resi 1-50, residues_1_50.csv

    Since:
        1.0.0

    See Also:
        export_group, export_objects
    """
    selection = _clean(selection)
    outfile = _clean(outfile)

    if not selection:
        plog(_TAG, "selection must be non-empty", "error")
        return 0
    if not outfile:
        plog(_TAG, "outfile must be non-empty", "error")
        return 0

    plog(_TAG, f"selection={selection!r} outfile={outfile!r}")

    try:
        atom_count = cmd.count_atoms(selection)
    except Exception as exc:  # noqa: BLE001
        plog(_TAG, f"invalid selection {selection!r}: {exc}", "error")
        return 0
    if atom_count == 0:
        plog(_TAG, f"selection {selection!r} contains no atoms", "warn")
        return 0

    residues: set[tuple[str, str, str]] = set()
    try:
        cmd.iterate(
            f"byres ({selection})",
            "residues.add((chain, resn, resi))",
            space={"residues": residues},
        )
    except Exception as exc:  # noqa: BLE001
        plog(_TAG, f"iteration failed: {exc}", "error")
        return 0

    if not residues:
        plog(_TAG, f"no residues in selection {selection!r}", "warn")
        return 0

    target = Path(outfile).expanduser()
    if target.parent and not target.parent.exists():
        try:
            target.parent.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            plog(_TAG, f"failed to create {target.parent}: {exc}", "error")
            return 0

    try:
        with target.open("w", newline="") as fh:
            writer = csv.writer(fh)
            writer.writerow(["chain", "resname", "resid"])
            for row in sorted(residues):
                writer.writerow(row)
    except OSError as exc:
        plog(_TAG, f"failed to write {target}: {exc}", "error")
        return 0

    plog(_TAG, f"wrote {len(residues)} residue(s) to {target}")
    return len(residues)
