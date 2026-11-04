"""Load molecules from SMILES strings or ``.smi`` files with RDKit conformers.

RDKit is an optional dependency; install it with ``pymolish_install_deps rdkit``.
"""

from __future__ import annotations

import os

from pymol import cmd

from ...core.cli import clean
from ...core.logging import plog

_TAG = "io.smiles"
_INSTALL_HINT = (
    "rdkit is required but is not installed. Install with: "
    "pymolish_install_deps rdkit (or pip install 'pymolish[rdkit]' "
    "in PyMOL's Python environment)."
)
_SMI_SUFFIXES = (".smi", ".smiles", ".txt")
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


def _read_entries(arg: str) -> list[tuple[str, str | None]]:
    """Return ``[(smiles, name_or_None)]`` from a SMILES string or a ``.smi`` file."""
    if not (os.path.isfile(arg) and arg.lower().endswith(_SMI_SUFFIXES)):
        return [(arg, None)]
    entries: list[tuple[str, str | None]] = []
    with open(arg, encoding="utf-8") as handle:
        for line in handle:
            parts = line.split()
            if parts and not parts[0].startswith("#"):
                entries.append((parts[0], parts[1] if len(parts) > 1 else None))
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


def load_smiles(
    smiles: str,
    name: str | None = None,
    n_conformers: int | str = 10,
    mode: str = "objects",
    seed: int | str = 42,
) -> list[str]:
    """Load a molecule from a SMILES string (or ``.smi`` file) with 3D conformers.

    Conformers are generated with RDKit ETKDGv3, force-field minimized
    (MMFF94, UFF fallback) and loaded without touching the disk.

    Args:
        smiles: SMILES string, or path to a ``.smi``/``.smiles``/``.txt`` file
            with one ``SMILES [name]`` entry per line (``#`` lines ignored).
        name: Object name. Defaults to an unused ``molNN`` name. For files the
            per-line name wins; otherwise this is used as the prefix.
        n_conformers: Maximum number of conformers (RMS pruning may yield fewer).
        mode: ``objects`` loads ``name_1 .. name_n`` grouped under ``name``;
            ``states`` loads all conformers as states of one object ``name``.
        seed: Random seed for reproducible embedding.

    Returns:
        Names of the objects created (empty on error).

    Examples:
        PyMOL> load_smiles CC(=O)Oc1ccccc1C(=O)O
        PyMOL> load_smiles CC(=O)Oc1ccccc1C(=O)O, aspirin, 5
        PyMOL> load_smiles c1ccccc1O, phenol, 20, states
        PyMOL> load_smiles ligands.smi, lig, 3

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
    smiles = clean(smiles)
    name = clean(name) if name else None
    mode = clean(mode).lower()
    n_conformers = max(1, int(n_conformers))
    if mode not in _MODES:
        plog(_TAG, f"mode must be one of {', '.join(_MODES)}; got {mode!r}", "error")
        return []

    entries = _read_entries(smiles)
    loaded: list[str] = []
    for smi, label in entries:
        if len(entries) == 1:
            obj = name or cmd.get_unused_name("mol")
        else:
            obj = label or cmd.get_unused_name(name or "mol")
        try:
            blocks = _conformer_blocks(smi, n_conformers, int(seed))
        except ValueError as exc:
            plog(_TAG, str(exc), "error")
            continue
        loaded.extend(_load_blocks(blocks, obj, mode == "states"))
        plog(_TAG, f"{obj}: {len(blocks)} conformer(s) as {mode}")
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
