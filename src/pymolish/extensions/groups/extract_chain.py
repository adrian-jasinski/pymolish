"""Extract specific chains from group objects."""

from __future__ import annotations

from pymol import cmd

from ...core.group_utils import GroupUtils
from ...core.logging import plog
from ...core.validators import coerce_bool

_TAG = "groups.extract_chain"


def _clean(value: str) -> str:
    """Strip one layer of surrounding quotes from a PyMOL command argument."""
    if not isinstance(value, str):
        return value
    return value.strip().strip("'\"")


def _resolve_targets(group_pattern: str) -> list[str]:
    """Return target objects for *group_pattern* using group → object → pattern."""
    if GroupUtils.is_group(group_pattern):
        objs = GroupUtils.get_group_objects(group_pattern) or []
        if objs:
            return list(objs)

    if GroupUtils.is_object(group_pattern):
        return [group_pattern]

    matches = GroupUtils.find_objects_by_pattern(group_pattern)
    return list(matches)


def extract_chain_from_group(
    group_pattern: str,
    chain: str,
    prefix: str = "chain_extract",
    add_to_group: bool | str | int = True,
) -> list[str]:
    """Extract a single chain from every object matching *group_pattern*.

    For each resolved target object creates a new object named
    ``<prefix>_<source>_<chain>`` containing only the specified chain.  If an
    object with that name already exists it is replaced.

    Args:
        group_pattern: Group name, object name, or wildcard pattern.
        chain: Chain identifier to extract (e.g. ``"A"``).
        prefix: Prefix for newly created object names (default
            ``"chain_extract"``).
        add_to_group: When truthy, collect extracted objects into a group
            named ``<group_pattern>_chain_<chain>`` (default ``True``).

    Returns:
        List of created object names.

    Examples:
        PyMOL> extract_chain_from_group my_group, A
        PyMOL> extract_chain_from_group protein_*, B, my_prefix
        PyMOL> extract_chain_from_group complex, C, chains, 0

    Since:
        1.0.0

    See Also:
        extract_chains_from_group
    """
    group_pattern = _clean(group_pattern)
    chain = _clean(chain)
    prefix = _clean(prefix)
    add_to_group = coerce_bool(add_to_group)

    if not chain:
        plog(_TAG, "chain must be non-empty", "error")
        return []

    targets = _resolve_targets(group_pattern)
    if not targets:
        # Fall back: treat group_pattern as a selection expression.
        try:
            atom_count = cmd.count_atoms(group_pattern)
        except Exception:  # noqa: BLE001
            atom_count = 0
        if atom_count == 0:
            plog(_TAG, f"no objects/groups/selection match {group_pattern!r}", "error")
            return []
        # Treat the pattern as a selection.
        targets = []
        sel_base = group_pattern.replace(" ", "_").replace("(", "").replace(")", "")
        selection_str = f"({group_pattern}) and chain {chain}"
        new_name = f"{prefix}_{sel_base}_{chain}"
        created = _create_chain_object(
            new_name, selection_str, group_pattern, chain, add_to_group
        )
        return [created] if created else []

    target_group = f"{group_pattern}_chain_{chain}" if add_to_group else ""

    plog(_TAG, f"extracting chain {chain!r} from {len(targets)} object(s)")
    created: list[str] = []
    for obj in targets:
        new_name = f"{prefix}_{obj}_{chain}"
        selection_str = f"({obj}) and chain {chain}"
        result = _create_chain_object(
            new_name, selection_str, target_group, chain, add_to_group
        )
        if result:
            created.append(result)

    if created:
        plog(_TAG, f"created {len(created)} object(s) with chain {chain!r}")
        if add_to_group and target_group:
            plog(_TAG, f"  -> group: {target_group!r}")
    else:
        plog(_TAG, f"chain {chain!r} not found in any target object", "warn")

    return created


def _create_chain_object(
    new_name: str,
    selection_str: str,
    target_group: str,
    chain: str,
    add_to_group: bool,
) -> str | None:
    """Create *new_name* from *selection_str*; add to *target_group* if requested."""
    # Replace existing object.
    if GroupUtils.is_object(new_name):
        try:
            cmd.delete(new_name)
        except Exception:  # noqa: BLE001
            pass

    try:
        atom_count = cmd.count_atoms(selection_str)
    except Exception as exc:  # noqa: BLE001
        plog(_TAG, f"cannot count atoms in {selection_str!r}: {exc}", "error")
        return None

    if atom_count == 0:
        plog(_TAG, f"selection {selection_str!r} has no atoms; skipping", "warn")
        return None

    try:
        cmd.create(new_name, selection_str)
        plog(_TAG, f"  created {new_name!r} ({atom_count} atoms)")
    except Exception as exc:  # noqa: BLE001
        plog(_TAG, f"failed to create {new_name!r}: {exc}", "error")
        return None

    if add_to_group and target_group:
        try:
            GroupUtils.add_to_group(target_group, new_name)
        except Exception as exc:  # noqa: BLE001
            plog(_TAG, f"could not add {new_name!r} to {target_group!r}: {exc}", "warn")

    return new_name


def extract_chains_from_group(
    group_pattern: str,
    chains: str,
    prefix: str = "chain_extract",
    add_to_group: bool | str | int = True,
) -> dict[str, list[str]]:
    """Extract multiple chains from every object matching *group_pattern*.

    Delegates each chain to :func:`extract_chain_from_group`.

    Args:
        group_pattern: Group name, object name, or wildcard pattern.
        chains: Comma-separated chain identifiers (e.g. ``"A,B,C"``).
        prefix: Prefix for newly created object names.
        add_to_group: When truthy, collect each chain's objects into its own
            group (default ``True``).

    Returns:
        Dict mapping each chain identifier to the list of created objects.

    Examples:
        PyMOL> extract_chains_from_group my_group, A,B
        PyMOL> extract_chains_from_group proteins, A,B,C
        PyMOL> extract_chains_from_group complex, A,B, my_prefix, 0

    Since:
        1.0.0

    See Also:
        extract_chain_from_group
    """
    group_pattern = _clean(group_pattern)
    prefix = _clean(prefix)
    add_to_group = coerce_bool(add_to_group)

    chain_list = [c.strip() for c in str(chains).split(",") if c.strip()]
    if not chain_list:
        plog(_TAG, "chains must be a non-empty comma-separated string", "error")
        return {}

    plog(_TAG, f"extracting chains {chain_list} from {group_pattern!r}")

    results: dict[str, list[str]] = {}
    for chain in chain_list:
        created = extract_chain_from_group(group_pattern, chain, prefix, add_to_group)
        results[chain] = created

    total = sum(len(v) for v in results.values())
    plog(_TAG, f"total objects created: {total}")
    return results
