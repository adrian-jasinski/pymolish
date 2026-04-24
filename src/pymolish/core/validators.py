"""Common argument validators shared across extension modules."""

from __future__ import annotations

from pathlib import Path

from pymol import cmd

from .logging import plog


def validate_directory(path: str) -> Path:
    """Return a resolved :class:`Path` if ``path`` is an existing directory.

    Args:
        path: Filesystem path to validate.

    Returns:
        Resolved absolute ``Path`` pointing at the directory.

    Raises:
        NotADirectoryError: ``path`` does not exist or is not a directory.
    """
    resolved = Path(path).expanduser().resolve()
    if not resolved.is_dir():
        raise NotADirectoryError(f"{path!r} is not an existing directory")
    return resolved


def validate_suffix(suffix: str) -> str:
    """Normalize a file suffix to a lowercase, dotless form.

    Args:
        suffix: Extension like ``"pdb"``, ``".pdb"``, or ``"PDB"``.

    Returns:
        The canonical lowercase suffix without a leading dot.

    Raises:
        ValueError: ``suffix`` is empty after stripping.
    """
    cleaned = suffix.strip().lstrip(".").lower()
    if not cleaned:
        raise ValueError("suffix must be a non-empty string")
    return cleaned


def validate_group_exists(group_name: str) -> bool:
    """Return ``True`` when ``group_name`` is a known PyMOL group."""
    if not group_name:
        return False
    try:
        return cmd.get_type(group_name) == "object:group"
    except Exception:  # noqa: BLE001 — PyMOL raises CmdException subclasses
        return False


def validate_object_exists(object_name: str) -> bool:
    """Return ``True`` when ``object_name`` refers to a loaded PyMOL object."""
    if not object_name:
        return False
    return object_name in set(cmd.get_object_list() or [])


def validate_selection(selection: str) -> bool:
    """Return ``True`` when ``selection`` is a non-empty PyMOL selection.

    Emits a warning via :func:`plog` when PyMOL rejects the selection syntax.
    """
    if not selection:
        return False
    try:
        return cmd.count_atoms(selection) > 0
    except Exception as exc:  # noqa: BLE001
        plog("validators", f"invalid selection {selection!r}: {exc}", "warn")
        return False


def coerce_bool(value: str | bool | int) -> bool:
    """Coerce PyMOL-style truthy values (``"1"``, ``"yes"``, ``True``) to ``bool``.

    Args:
        value: Incoming value from a PyMOL command argument.

    Returns:
        ``True`` for ``1``, ``"1"``, ``"true"``, ``"yes"``, ``"on"`` (case-insensitive)
        and any Python truthy bool/int. ``False`` otherwise.
    """
    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        return value != 0
    return value.strip().lower() in {"1", "true", "yes", "on", "y", "t"}
