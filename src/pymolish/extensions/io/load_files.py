"""Batch loading of structure files from directories."""

from __future__ import annotations

import fnmatch
import glob
import os
from pathlib import Path

from pymol import cmd

from pymolish.core.group_utils import GroupUtils
from pymolish.core.logging import plog
from pymolish.core.validators import coerce_bool, validate_suffix

_TAG = "io.load"


def _strip_quotes(value: str | None) -> str | None:
    """Strip one layer of surrounding quotes if present."""
    if not isinstance(value, str):
        return value
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
        return value[1:-1]
    return value


def _normalize_exclude_subdirs(value: str | list[str] | None) -> list[str]:
    """Normalize ``exclude_subdirs`` to a list of non-empty directory names."""
    if value is None:
        return []
    if isinstance(value, str):
        return [part.strip() for part in value.split(",") if part.strip()]
    return [str(part).strip() for part in value if str(part).strip()]


def _collect_files(
    dir_path: Path,
    suffix: str,
    *,
    recursive: bool,
    max_depth: int,
    excluded: list[str],
) -> list[Path]:
    """Return sorted paths matching ``*.{suffix}`` under ``dir_path``."""
    dot_suffix = f".{suffix.lower()}"
    if not recursive:
        return sorted(Path(p) for p in glob.glob(str(dir_path / f"*.{suffix}")))

    results: list[Path] = []
    base = str(dir_path)
    for root, dirs, files in os.walk(base):
        depth = root[len(base) :].count(os.sep)
        if depth >= max_depth:
            dirs[:] = []
            continue
        dirs[:] = [d for d in dirs if d not in excluded]
        for name in files:
            if name.lower().endswith(dot_suffix):
                results.append(Path(root) / name)
    return sorted(results)


def _display_name(path: Path, root: Path, recursive: bool) -> str:
    """Return the string shown to the user for ``path`` relative to ``root``."""
    return str(path.relative_to(root)) if recursive else path.name


def _object_name_for(path: Path, root: Path, recursive: bool) -> str:
    """Derive a PyMOL object base name from ``path`` (flattening subdirs)."""
    if recursive:
        return str(path.relative_to(root).with_suffix("")).replace(os.sep, "_")
    return path.stem


def load_files(
    dir_name: str = ".",
    suffix: str = "pdb",
    group_name: str | None = None,
    prefix: str = "",
    name_filter: str | None = None,
    recursive: bool | str | int = False,
    exclude_subdirs: str | list[str] | None = None,
    max_depth: int = 3,
    verbose: bool | str | int = True,
) -> list[str]:
    """Load multiple structure files from a directory into PyMOL.

    Scans ``dir_name`` for files with the given ``suffix``, loads each as a
    PyMOL object, resolves naming conflicts with a numeric suffix, and
    optionally groups the loaded objects.

    Args:
        dir_name: Directory path to load from (default: current directory).
        suffix: File extension without leading dot (e.g. ``"pdb"``, ``"cif"``).
        group_name: Optional group for loaded objects.
        prefix: String prepended to each object name.
        name_filter: Wildcard pattern applied to basenames (e.g. ``"model_*"``).
        recursive: When truthy, walk subdirectories up to ``max_depth``.
        exclude_subdirs: Directory names to skip during recursive walks.
        max_depth: Maximum recursion depth (default: 3).
        verbose: When truthy, print per-file progress.

    Returns:
        List of successfully loaded object names.

    Examples:
        PyMOL> load_files
        PyMOL> load_files /tmp, sdf
        PyMOL> load_files ., pdb, my_proteins
        PyMOL> load_files ., pdb, , , , 1, "traj, cache"

    Since:
        1.0.0

    See Also:
        load_recursive, list_loadable_files, export_group
    """
    recursive = coerce_bool(recursive)
    verbose = coerce_bool(verbose)
    name_filter = _strip_quotes(name_filter)
    dir_path = Path(_strip_quotes(dir_name) or ".").expanduser()

    if verbose:
        plog(_TAG, f"loading from {dir_path} (suffix={suffix!r})")
        if group_name:
            plog(_TAG, f"group: {group_name}")
        if prefix:
            plog(_TAG, f"prefix: {prefix}")
        if name_filter:
            plog(_TAG, f"filter: {name_filter}")
        if recursive:
            plog(_TAG, f"recursive: True (max_depth={max_depth})")

    if not dir_path.is_dir():
        plog(_TAG, f"{dir_path} is not an existing directory", "error")
        return []

    try:
        suffix = validate_suffix(suffix)
    except ValueError as exc:
        plog(_TAG, str(exc), "error")
        return []

    excluded = _normalize_exclude_subdirs(exclude_subdirs) if recursive else []
    if recursive and excluded and verbose:
        plog(_TAG, f"excluding subdirs: {excluded}")

    paths = _collect_files(
        dir_path,
        suffix,
        recursive=recursive,
        max_depth=max_depth,
        excluded=excluded,
    )
    if not paths:
        pattern = f"*.{suffix}" + (" (recursive)" if recursive else "")
        plog(_TAG, f"no files matched {pattern}")
        return []

    if name_filter:
        paths = [p for p in paths if fnmatch.fnmatch(p.stem, name_filter)]
        if not paths:
            plog(_TAG, f"no files matched name_filter={name_filter!r}")
            return []

    if verbose:
        plog(_TAG, f"found {len(paths)} file(s) to load")

    existing = set(GroupUtils.get_all_objects())
    loaded: list[str] = []
    failed: list[tuple[Path, str]] = []

    for idx, path in enumerate(paths, start=1):
        base = _object_name_for(path, dir_path, recursive)
        desired = f"{prefix}{base}"
        name = GroupUtils.unique_name(desired, list(existing))
        try:
            if verbose:
                display = _display_name(path, dir_path, recursive)
                plog(_TAG, f"({idx}/{len(paths)}) {display} -> {name}")
            cmd.load(str(path), name)
            existing.add(name)
            loaded.append(name)
        except Exception as exc:  # noqa: BLE001
            plog(_TAG, f"failed to load {path.name}: {exc}", "error")
            failed.append((path, str(exc)))

    if group_name and loaded:
        try:
            GroupUtils.ensure_group(group_name, loaded)
        except Exception as exc:  # noqa: BLE001
            plog(_TAG, f"failed to group into {group_name!r}: {exc}", "warn")

    if verbose:
        plog(_TAG, f"loaded {len(loaded)} file(s); {len(failed)} failed")
        if group_name and loaded:
            plog(_TAG, f"grouped under: {group_name}")

    return loaded


def load_recursive(
    dir_name: str = ".",
    suffix: str = "pdb",
    group_name: str | None = None,
    prefix: str = "",
    name_filter: str | None = None,
    max_depth: int = 3,
    verbose: bool | str | int = True,
) -> list[str]:
    """Recursively load files from ``dir_name`` and subdirectories.

    Convenience wrapper around :func:`load_files` with ``recursive=True``.

    Args:
        dir_name: Root directory to walk.
        suffix: File extension without leading dot.
        group_name: Optional group for loaded objects.
        prefix: Object-name prefix.
        name_filter: Basename wildcard filter.
        max_depth: Maximum recursion depth (default: 3).
        verbose: When truthy, print per-file progress.

    Returns:
        List of successfully loaded object names.

    Examples:
        PyMOL> load_recursive
        PyMOL> load_recursive /data, sdf, ligands
        PyMOL> load_recursive ., cif, , , model_*

    Since:
        1.0.0

    See Also:
        load_files, list_loadable_files
    """
    return load_files(
        dir_name=dir_name,
        suffix=suffix,
        group_name=group_name,
        prefix=prefix,
        name_filter=name_filter,
        recursive=True,
        exclude_subdirs=None,
        max_depth=max_depth,
        verbose=verbose,
    )


def list_loadable_files(
    dir_name: str = ".",
    suffix: str = "pdb",
    recursive: bool | str | int = False,
    name_filter: str | None = None,
    exclude_subdirs: str | list[str] | None = None,
    max_depth: int = 3,
) -> list[str]:
    """Preview files that would be loaded without actually loading them.

    Args:
        dir_name: Directory path to search.
        suffix: File extension without leading dot.
        recursive: When truthy, walk subdirectories up to ``max_depth``.
        name_filter: Basename wildcard filter.
        exclude_subdirs: Directory names to skip during recursive walks.
        max_depth: Maximum recursion depth (default: 3).

    Returns:
        List of file paths that would be loaded (strings, sorted).

    Examples:
        PyMOL> list_loadable_files
        PyMOL> list_loadable_files /tmp, sdf, 1
        PyMOL> list_loadable_files ., pdb, 1, , traj

    Since:
        1.0.0

    See Also:
        load_files, load_recursive
    """
    recursive = coerce_bool(recursive)
    name_filter = _strip_quotes(name_filter)
    dir_path = Path(_strip_quotes(dir_name) or ".").expanduser()

    if not dir_path.is_dir():
        plog(_TAG, f"{dir_path} is not an existing directory", "error")
        return []

    try:
        suffix = validate_suffix(suffix)
    except ValueError as exc:
        plog(_TAG, str(exc), "error")
        return []

    excluded = _normalize_exclude_subdirs(exclude_subdirs) if recursive else []
    paths = _collect_files(
        dir_path,
        suffix,
        recursive=recursive,
        max_depth=max_depth,
        excluded=excluded,
    )
    if name_filter:
        paths = [p for p in paths if fnmatch.fnmatch(p.stem, name_filter)]

    if not paths:
        plog(_TAG, f"no {suffix} files found")
        return []

    plog(_TAG, f"{len(paths)} {suffix} file(s) in {dir_path}")
    for idx, path in enumerate(paths, start=1):
        display = _display_name(path, dir_path, recursive)
        plog(_TAG, f"  {idx:>3}. {display}")
    return [str(p) for p in paths]
