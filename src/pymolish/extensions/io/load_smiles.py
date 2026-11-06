"""Load molecules from SMILES strings or text/CSV files with RDKit conformers.

RDKit is an optional dependency; install it with ``pymolish_install_deps rdkit``.
"""

from __future__ import annotations

import os

from pymol import cmd

from ...core.cli import clean
from ...core.group_utils import GroupUtils
from ...core.logging import plog

_TAG = "io.smiles"
_INSTALL_HINT = (
    "rdkit is required but is not installed. Install with: "
    "pymolish_install_deps rdkit (or pip install 'pymolish[rdkit]' "
    "in PyMOL's Python environment)."
)
_SMI_SUFFIXES = (".smi", ".smiles", ".txt", ".csv")
_MODES = ("objects", "states")


def _rdkit():
    """Return ``(Chem, AllChem)`` or raise ``ImportError`` with an install hint."""
    try:
        from rdkit import Chem, RDLogger
        from rdkit.Chem import AllChem
    except ImportError as exc:
        raise ImportError(_INSTALL_HINT) from exc
    # ponytail: rdkit writes parse errors to stderr; plog reports them instead.
    RDLogger.DisableLog("rdApp.*")
    return Chem, AllChem


def is_smiles(text: str) -> bool:
    """Return ``True`` if *text* is one whitespace-free token RDKit parses.

    Raises:
        ImportError: If RDKit is not installed.
    """
    text = text.strip()
    if not text or len(text.split()) != 1:
        return False
    chem, _ = _rdkit()
    return chem.MolFromSmiles(text) is not None


def _read_entries(arg: str, name_column: int) -> list[tuple[str, str | None]]:
    """Read inline SMILES or text/CSV rows with an optional one-based name column."""
    path = os.path.expanduser(arg)
    if not (path.lower().endswith(_SMI_SUFFIXES) or os.path.isfile(path)):
        return [(arg, None)]
    with open(path, encoding="utf-8-sig", newline="") as handle:
        lines = handle.readlines()
    if path.lower().endswith(".csv"):
        try:
            import csv
        except ImportError as exc:
            raise ValueError(
                "Python's standard-library csv module is unavailable. "
                "Check or repair PyMOL's Python standard library."
            ) from exc
        sample = next(
            (
                line
                for line in lines
                if line.strip() and not line.lstrip().startswith("#")
            ),
            "",
        )
        try:
            delimiter = csv.Sniffer().sniff(sample, delimiters=",;").delimiter
        except csv.Error:
            delimiter = ","  # A file may contain only the SMILES column.
        try:
            rows = list(
                csv.reader(
                    lines, delimiter=delimiter, skipinitialspace=True, strict=True
                )
            )
        except csv.Error as exc:
            raise ValueError(f"malformed CSV: {exc}") from exc
    else:
        rows = [
            line.rstrip("\r\n").split("\t") if "\t" in line else line.split()
            for line in lines
        ]

    entries: list[tuple[str, str | None]] = []
    first_row = True
    for parts in rows:
        if not parts or not parts[0].strip() or parts[0].lstrip().startswith("#"):
            continue
        smi = parts[0].strip()
        if first_row and smi.lower() == "smiles":
            first_row = False
            continue
        first_row = False
        label = (
            parts[name_column - 1].strip() if 0 < name_column <= len(parts) else None
        )
        entries.append((smi, label or None))
    return entries


def _conformer_blocks(smiles: str, n_conformers: int, seed: int) -> list[str]:
    """Return MOL blocks for up to *n_conformers* optimized 3D conformers.

    Raises:
        ValueError: If the SMILES is invalid or cannot be embedded in 3D.
    """
    chem, allchem = _rdkit()
    mol = chem.MolFromSmiles(smiles)
    if mol is None:
        raise ValueError(f"invalid SMILES: {smiles!r}")
    mol = chem.AddHs(mol)
    params = allchem.ETKDGv3()
    params.randomSeed = seed
    params.pruneRmsThresh = 0.5
    cids = list(allchem.EmbedMultipleConfs(mol, numConfs=n_conformers, params=params))
    if not cids:
        # ponytail: macrocycles/strained rings can fail ETKDG; random coords rescue
        params.useRandomCoords = True
        cids = list(
            allchem.EmbedMultipleConfs(mol, numConfs=n_conformers, params=params)
        )
    if not cids:
        raise ValueError(f"could not generate 3D coordinates for {smiles!r}")
    if allchem.MMFFHasAllMoleculeParams(mol):
        allchem.MMFFOptimizeMoleculeConfs(mol, maxIters=500)
    else:
        allchem.UFFOptimizeMoleculeConfs(mol, maxIters=500)
    return [chem.MolToMolBlock(mol, confId=cid) for cid in cids]


def _load_blocks(blocks: list[str], name: str, as_states: bool) -> list[str]:
    """Load MOL *blocks* as states of ``name`` or as grouped ``name_i`` objects."""
    if as_states or len(blocks) == 1:
        for state, block in enumerate(blocks, 1):
            cmd.read_molstr(block, name, state=state, discrete=0)
        return [name]
    names = [f"{name}_{i}" for i in range(1, len(blocks) + 1)]
    for obj, block in zip(names, blocks, strict=True):
        cmd.read_molstr(block, obj)
    cmd.group(name, " ".join(names))
    return names


def _available_name(
    desired: str, count: int, as_states: bool, existing: set[str]
) -> str:
    """Avoid collisions for both the molecule name and its conformer objects."""
    base = cmd.get_legal_name(desired) or "mol"
    taken = set(existing)
    while True:
        name = GroupUtils.unique_name(base, list(taken))
        if as_states or count == 1:
            return name
        if not any(f"{name}_{i}" in existing for i in range(1, count + 1)):
            return name
        taken.add(name)


def load_smiles(
    smiles: str | os.PathLike[str],
    name: str | None = None,
    n_conformers: int | str = 10,
    mode: str = "objects",
    seed: int | str = 42,
    group_name: str | None = None,
    name_column: int | str = 2,
) -> list[str]:
    """Load molecules from inline SMILES or a text/CSV file with 3D conformers.

    Conformers are generated with RDKit ETKDGv3, force-field minimized
    (MMFF94, UFF fallback) and loaded without touching the disk.

    Args:
        smiles: SMILES string or file path (quoted paths and ``~`` supported).
            Existing files and paths ending in ``.smi``, ``.smiles``, ``.txt``,
            or ``.csv`` are detected automatically. Text files use spaces/tabs;
            CSV uses commas or semicolons (auto-detected, quotes supported).
            Column 1 contains SMILES. Blank lines, ``#`` comments and an optional
            initial ``SMILES`` header are skipped; unused metadata is ignored.
            Files must be UTF-8 (an optional BOM is accepted).
        name: Fallback object name for one molecule, or naming prefix for multiple
            molecules. Defaults to an unused ``molNN`` name. File labels take
            precedence. Names are made legal in PyMOL and unique in the session.
        n_conformers: Maximum number of conformers (RMS pruning may yield fewer).
        mode: ``objects`` loads ``name_1 .. name_n`` grouped under ``name``;
            ``states`` loads all conformers as states of one object ``name``.
        seed: Random seed for reproducible embedding.
        group_name: Optional parent group for loaded molecules. Existing groups
            are reused; conformer groups remain nested beneath this group.
        name_column: One-based file column for object names/IDs (default: 2).
            Use ``0`` to ignore file names. Missing/empty names use ``name`` or
            an unused ``molNN`` name. Does not affect inline SMILES.

    Returns:
        Names of successfully created objects. Invalid molecules are skipped;
        input errors or files with no molecules return an empty list.

    Examples:
        PyMOL> load_smiles CC(=O)Oc1ccccc1C(=O)O
        PyMOL> load_smiles CC(=O)Oc1ccccc1C(=O)O, aspirin, 5
        PyMOL> load_smiles c1ccccc1O, phenol, 20, states
        PyMOL> load_smiles ligands.smi, lig, 3
        PyMOL> load_smiles ligands.csv, group_name=ligands, name_column=3
        PyMOL> load_smiles ligands.txt, name=lig, name_column=0

    Since:
        0.1.24

    See Also:
        paste_smiles, pymolish_install_deps
    """
    try:
        _rdkit()
    except ImportError as exc:
        plog(_TAG, f"load_smiles cannot run: {exc}", "error")
        return []
    smiles = clean(os.fspath(smiles))
    name = clean(name) if name else None
    group_name = clean(group_name) if group_name else None
    mode = clean(mode).lower()
    try:
        n_conformers = max(1, int(n_conformers))
        seed = int(seed)
        name_column = int(name_column)
        if name_column < 0:
            raise ValueError("name_column must be 0 or a positive column number")
    except (TypeError, ValueError) as exc:
        plog(_TAG, f"invalid numeric argument: {exc}", "error")
        return []
    if mode not in _MODES:
        plog(_TAG, f"mode must be one of {', '.join(_MODES)}; got {mode!r}", "error")
        return []

    try:
        entries = _read_entries(smiles, name_column)
    except (OSError, ValueError) as exc:
        plog(_TAG, f"could not read {smiles!r}: {exc}", "error")
        return []
    if not entries:
        plog(_TAG, "no SMILES entries found", "warn")
        return []
    existing = set(cmd.get_names() or [])
    if group_name:
        group_name = cmd.get_legal_name(group_name)
        if not group_name or (
            group_name in existing and not GroupUtils.is_group(group_name)
        ):
            plog(_TAG, f"cannot use {group_name!r} as a parent group", "error")
            return []
        existing.add(group_name)
    loaded: list[str] = []
    members: list[str] = []
    as_states = mode == "states"
    for smi, label in entries:
        try:
            blocks = _conformer_blocks(smi, n_conformers, seed)
        except ValueError as exc:
            plog(_TAG, str(exc), "error")
            continue
        desired = label or (name if len(entries) == 1 else None)
        desired = desired or cmd.get_unused_name(name or "mol")
        obj = _available_name(desired, len(blocks), as_states, existing)
        objects = _load_blocks(blocks, obj, as_states)
        loaded.extend(objects)
        members.append(obj)
        existing.update([obj, *objects])
        plog(_TAG, f"{obj}: {len(blocks)} conformer(s) as {mode}")
    if group_name and members:
        try:
            GroupUtils.ensure_group(group_name, members)
        except Exception as exc:  # noqa: BLE001 — PyMOL command failures
            plog(_TAG, f"failed to group into {group_name!r}: {exc}", "warn")
    return loaded


def _clipboard_text() -> str:
    """Return the system clipboard text (Qt first, tkinter fallback, else '')."""
    try:
        from pymol.Qt import QtWidgets

        app = QtWidgets.QApplication.instance()
        if app is not None:
            return app.clipboard().text()
    except ImportError:
        pass
    try:
        import tkinter

        root = tkinter.Tk()
        root.withdraw()
        try:
            return root.clipboard_get()
        finally:
            root.destroy()
    except Exception:  # noqa: BLE001 — headless: no clipboard at all
        return ""


def paste_smiles(n_conformers: int | str = 10, mode: str = "objects") -> list[str]:
    """Load the clipboard as a molecule if it is a valid SMILES.

    Bound to ``Ctrl+V`` while the 3D viewer has focus (the command line keeps
    its normal paste behaviour). Non-SMILES text is ignored with a message.

    Args:
        n_conformers: Maximum number of conformers to generate.
        mode: ``objects`` (default) or ``states``; see :func:`load_smiles`.

    Returns:
        Names of the objects created (empty if nothing was loaded).

    Examples:
        PyMOL> paste_smiles
        PyMOL> paste_smiles 3, states

    Since:
        0.1.24

    See Also:
        load_smiles, pymolish_install_deps
    """
    try:
        _rdkit()
    except ImportError as exc:
        plog(_TAG, f"paste_smiles cannot run: {exc}", "error")
        return []
    text = _clipboard_text().strip()
    if not text:
        plog(_TAG, "clipboard is empty")
        return []
    if not is_smiles(text):
        plog(_TAG, f"clipboard text is not a SMILES: {text[:40]!r}")
        return []
    return load_smiles(text, n_conformers=n_conformers, mode=mode)
