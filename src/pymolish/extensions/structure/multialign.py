"""Multiple structure alignment with RMSD statistics."""

from __future__ import annotations

import fnmatch
import statistics

from pymol import cmd

from pymolish.core.logging import plog

_TAG = "structure.multialign"


def _clean(value: str) -> str:
    """Strip one layer of surrounding quotes from PyMOL command arguments."""
    if not isinstance(value, str):
        return value
    return value.strip().strip("'\"")


def _get_objects_from_group_or_selection(group_or_selection: str) -> list[str]:
    """Return object names contained in a group, selection, or wildcard pattern.

    Tries four strategies in order:
    1. ``cmd.get_names("objects", group_or_selection)`` — direct group lookup.
    2. Per-object atom-count intersection with the selection.
    3. fnmatch wildcard against all object names.
    4. Single-object / generic selection fallback.

    Args:
        group_or_selection: PyMOL group name, selection string, or glob pattern.

    Returns:
        Deduplicated, ordered list of matching object names (may be empty).
    """
    # Strategy 1: direct group membership
    try:
        members = cmd.get_names("objects", group_or_selection)
        if members:
            return list(members)
    except Exception:  # noqa: BLE001
        pass

    # Strategy 2: selection intersection
    try:
        all_objects = cmd.get_names("objects") or []
        matched = []
        for obj in all_objects:
            try:
                if cmd.count_atoms(f"({group_or_selection}) and {obj}") > 0:
                    matched.append(obj)
            except Exception:  # noqa: BLE001
                pass
        if matched:
            return matched
    except Exception:  # noqa: BLE001
        pass

    # Strategy 3: wildcard / glob pattern
    if "*" in group_or_selection or "?" in group_or_selection:
        try:
            all_objects = cmd.get_names("objects") or []
            matched = [
                obj for obj in all_objects if fnmatch.fnmatch(obj, group_or_selection)
            ]
            if matched:
                return matched
        except Exception:  # noqa: BLE001
            pass

    # Strategy 4: single object or valid selection
    try:
        if cmd.count_atoms(group_or_selection) > 0:
            return [group_or_selection]
    except Exception:  # noqa: BLE001
        pass

    return []


def _align_to_target(mobile: str, target: str) -> float | None:
    """Align *mobile* onto *target* and return RMSD (Å), or ``None`` on failure.

    Args:
        mobile: PyMOL object name to align.
        target: PyMOL object name used as the reference.

    Returns:
        RMSD value in Ångströms, or ``None`` when alignment fails.
    """
    try:
        result = cmd.align(mobile, target, quiet=1)
        if result and len(result) >= 1:
            return result[0]
    except Exception as exc:  # noqa: BLE001
        plog(_TAG, f"align {mobile!r} → {target!r} failed: {exc}", "warn")
    return None


def multialign(
    group_or_selection: str,
    target: str,
    verbose: bool | str | int = True,
) -> dict[str, float]:
    """Align multiple structures to a reference and report RMSD statistics.

    Resolves *group_or_selection* to a list of PyMOL objects (group members,
    selection intersection, or wildcard pattern), aligns each to *target* via
    :pymol:`align`, and prints a summary with min/max/mean/median RMSD.

    Args:
        group_or_selection: Group name, selection, or glob pattern containing
            the structures to align.
        target: PyMOL object name used as the alignment reference.
        verbose: When truthy, print per-structure progress and the final
            statistics table.

    Returns:
        Mapping of ``{object_name: rmsd}`` for every successful alignment.
        Failed structures are omitted.

    Examples:
        PyMOL> multialign my_structures, reference_protein
        PyMOL> multialign protein_*, template_1
        PyMOL> multialign Estrogen, 1A52, 0

    Since:
        1.0.0

    See Also:
        list_objects_with_prefix
    """
    from pymolish.core.validators import coerce_bool

    verbose = coerce_bool(verbose)
    group_or_selection = _clean(group_or_selection)
    target = _clean(target)

    if not target:
        plog(_TAG, "target must be non-empty", "error")
        return {}

    if cmd.count_atoms(target) == 0:
        plog(_TAG, f"target {target!r} not found or has no atoms", "error")
        return {}

    objects = _get_objects_from_group_or_selection(group_or_selection)
    if not objects:
        plog(
            _TAG,
            f"no objects found for {group_or_selection!r}; "
            f"available: {cmd.get_names('objects')}",
            "error",
        )
        return {}

    if verbose:
        plog(_TAG, f"aligning {len(objects)} object(s) to {target!r}")

    results: dict[str, float] = {}
    n = len(objects)
    for idx, obj in enumerate(objects, start=1):
        if obj == target:
            if verbose:
                plog(_TAG, f"({idx}/{n}) {obj!r} — skipped (same as target)")
            continue
        rmsd = _align_to_target(obj, target)
        if rmsd is not None:
            results[obj] = rmsd
            if verbose:
                plog(_TAG, f"({idx}/{n}) {obj!r} → RMSD {rmsd:.3f} Å")
        else:
            if verbose:
                plog(_TAG, f"({idx}/{n}) {obj!r} — alignment failed", "warn")

    if verbose and results:
        rmsd_vals = list(results.values())
        best = min(rmsd_vals)
        worst = max(rmsd_vals)
        avg = statistics.mean(rmsd_vals)
        med = statistics.median(rmsd_vals)
        plog(
            _TAG,
            f"summary: n={len(results)}, best={best:.3f}, worst={worst:.3f}, "
            f"mean={avg:.3f}, median={med:.3f} Å",
        )

    if not results and verbose:
        plog(_TAG, "no successful alignments", "warn")

    return results


def list_objects_with_prefix(prefix: str = "") -> list[str]:
    """List all PyMOL objects whose names start with *prefix*.

    Args:
        prefix: Name prefix to filter by. When empty, all objects are returned.

    Returns:
        Matching object names (sorted).

    Examples:
        PyMOL> list_objects_with_prefix protein_
        PyMOL> list_objects_with_prefix chain_A
        PyMOL> list_objects_with_prefix

    Since:
        1.0.0

    See Also:
        multialign
    """
    prefix = _clean(prefix) or ""
    all_objects = cmd.get_names("objects") or []
    matched = (
        sorted(obj for obj in all_objects if obj.startswith(prefix))
        if prefix
        else sorted(all_objects)
    )
    plog(_TAG, f"objects{f' with prefix {prefix!r}' if prefix else ''}: {matched}")
    return matched
