"""Export PyMOL objects and groups to structure files."""

from __future__ import annotations

from pathlib import Path

from pymol import cmd

from ...core.group_utils import GroupUtils
from ...core.logging import plog
from ...core.validators import coerce_bool

_TAG = "io.export"
_FORMATS = {"cif", "pdb", "fasta"}


def _clean(value: str) -> str:
    """Strip one layer of surrounding quotes from PyMOL command arguments."""
    if not isinstance(value, str):
        return value
    return value.strip().strip("'\"")


def _ensure_output_dir(output_dir: Path) -> bool:
    """Create ``output_dir`` if missing. Return ``False`` on failure."""
    if output_dir.is_dir():
        return True
    try:
        output_dir.mkdir(parents=True, exist_ok=True)
        plog(_TAG, f"created output directory {output_dir}")
        return True
    except OSError as exc:
        plog(_TAG, f"failed to create {output_dir}: {exc}", "error")
        return False


def _save_object(obj_name: str, output_path: Path, format_type: str) -> bool:
    """Save a single PyMOL object. Return True on success."""
    try:
        if format_type == "fasta":
            cmd.save(str(output_path), obj_name, format="fasta")
        else:
            cmd.save(str(output_path), obj_name)
        plog(_TAG, f"exported {obj_name} -> {output_path}")
        return True
    except Exception as exc:  # noqa: BLE001
        plog(_TAG, f"failed to export {obj_name}: {exc}", "error")
        return False


def export_group(
    group_name: str,
    output_dir: str = ".",
    format_type: str = "cif",
    overwrite: bool | str | int = False,
) -> list[str]:
    """Export all objects in a PyMOL group to individual structure files.

    Args:
        group_name: Name of the PyMOL group to export.
        output_dir: Destination directory (created if missing).
        format_type: Output format — ``"cif"``, ``"pdb"``, or ``"fasta"``.
        overwrite: When truthy, overwrite existing files at the destination.

    Returns:
        List of paths written (strings).

    Examples:
        PyMOL> export_group my_structures
        PyMOL> export_group proteins, ., pdb
        PyMOL> export_group sequences, ., fasta
        PyMOL> export_group models, ./exports, cif, 1

    Since:
        1.0.0

    See Also:
        export_objects, export_by_pattern
    """
    group_name = _clean(group_name)
    output_dir = _clean(output_dir)
    format_type = _clean(format_type).lower()
    overwrite = coerce_bool(overwrite)

    if format_type not in _FORMATS:
        plog(_TAG, f"invalid format {format_type!r}; use cif|pdb|fasta", "error")
        return []

    members = GroupUtils.get_group_objects(group_name)
    if members is None:
        plog(_TAG, f"group {group_name!r} not found", "error")
        return []
    if not members:
        plog(_TAG, f"group {group_name!r} is empty", "warn")
        return []

    out_path = Path(output_dir).expanduser()
    if not _ensure_output_dir(out_path):
        return []

    plog(
        _TAG,
        f"exporting {len(members)} object(s) from {group_name!r} as {format_type}",
    )

    written: list[str] = []
    skipped = 0
    for obj_name in members:
        if not GroupUtils.is_object(obj_name):
            plog(_TAG, f"object {obj_name!r} not found; skipping", "warn")
            skipped += 1
            continue
        target = out_path / f"{obj_name}.{format_type}"
        if target.exists() and not overwrite:
            plog(_TAG, f"{target} exists; skipping (overwrite=1 to replace)")
            skipped += 1
            continue
        if _save_object(obj_name, target, format_type):
            written.append(str(target))

    plog(
        _TAG,
        f"done: {len(written)} written, {skipped} skipped, "
        f"{len(members) - len(written) - skipped} failed",
    )
    return written


def export_objects(
    object_names: str | list[str],
    output_dir: str = ".",
    format_type: str = "cif",
    overwrite: bool | str | int = False,
) -> list[str]:
    """Export explicit PyMOL objects to structure files.

    Args:
        object_names: Comma-separated string or list of object names.
        output_dir: Destination directory (created if missing).
        format_type: ``"cif"``, ``"pdb"``, or ``"fasta"``.
        overwrite: When truthy, overwrite existing files.

    Returns:
        List of paths written (strings).

    Examples:
        PyMOL> export_objects obj1,obj2,obj3
        PyMOL> export_objects obj1,obj2, ./out, pdb

    Since:
        1.0.0

    See Also:
        export_group, export_by_pattern
    """
    if isinstance(object_names, str):
        names = [n.strip() for n in _clean(object_names).split(",") if n.strip()]
    else:
        names = [str(n).strip() for n in object_names if str(n).strip()]

    output_dir = _clean(output_dir)
    format_type = _clean(format_type).lower()
    overwrite = coerce_bool(overwrite)

    if format_type not in _FORMATS:
        plog(_TAG, f"invalid format {format_type!r}; use cif|pdb|fasta", "error")
        return []

    out_path = Path(output_dir).expanduser()
    if not _ensure_output_dir(out_path):
        return []

    plog(_TAG, f"exporting {len(names)} object(s) as {format_type}")

    written: list[str] = []
    skipped = 0
    for obj_name in names:
        if not GroupUtils.is_object(obj_name):
            plog(_TAG, f"object {obj_name!r} not found; skipping", "warn")
            skipped += 1
            continue
        target = out_path / f"{obj_name}.{format_type}"
        if target.exists() and not overwrite:
            plog(_TAG, f"{target} exists; skipping")
            skipped += 1
            continue
        if _save_object(obj_name, target, format_type):
            written.append(str(target))

    plog(
        _TAG,
        f"done: {len(written)} written, {skipped} skipped, "
        f"{len(names) - len(written) - skipped} failed",
    )
    return written


def export_by_pattern(
    pattern: str,
    output_dir: str = ".",
    format_type: str = "cif",
    overwrite: bool | str | int = False,
) -> list[str]:
    """Export all objects whose names match ``pattern``.

    Args:
        pattern: Wildcard pattern (``*`` and ``?`` supported).
        output_dir: Destination directory (created if missing).
        format_type: ``"cif"``, ``"pdb"``, or ``"fasta"``.
        overwrite: When truthy, overwrite existing files.

    Returns:
        List of paths written (strings).

    Examples:
        PyMOL> export_by_pattern protein_*
        PyMOL> export_by_pattern chain_*, ./out, pdb

    Since:
        1.0.0

    See Also:
        export_group, export_objects
    """
    pattern = _clean(pattern)
    matches = GroupUtils.find_objects_by_pattern(pattern)
    if not matches:
        plog(_TAG, f"no objects matched {pattern!r}")
        return []
    plog(_TAG, f"{len(matches)} object(s) matched {pattern!r}")
    return export_objects(matches, output_dir, format_type, overwrite)


__all__ = [
    "export_by_pattern",
    "export_group",
    "export_objects",
]
