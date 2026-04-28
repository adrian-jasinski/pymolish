"""Cluster ligands by spatial position into PyMOL groups.

Heavy dependency: numpy.  All numpy usage is gated inside functions behind a
``try/except ImportError`` guard.  Install with ``pip install pymolish[numpy]``.
"""

from __future__ import annotations

from pymol import cmd

from ...core.logging import plog
from ...core.validators import coerce_bool

_TAG = "structure.cluster_ligands"


def _clean(value: str) -> str:
    """Strip one layer of surrounding quotes from PyMOL command arguments."""
    if not isinstance(value, str):
        return value
    return value.strip().strip("'\"")


def _resolve_ligand_objects(source: str) -> list[str]:
    """Resolve *source* (group or selection) to a list of object names.

    Args:
        source: PyMOL group name or selection expression.

    Returns:
        List of object names contained in or matching *source*.
    """
    # Strategy 1: group/object list
    try:
        members = cmd.get_object_list(f"({source})")
        if members:
            return list(members)
    except Exception:  # noqa: BLE001
        pass

    # Strategy 2: atom-count intersection per object
    try:
        all_objects = cmd.get_object_list("all") or []
        matched = []
        for obj in all_objects:
            try:
                if cmd.count_atoms(f"({obj}) and ({source})") > 0:
                    matched.append(obj)
            except Exception:  # noqa: BLE001
                pass
        return matched
    except Exception:  # noqa: BLE001
        return []


def _compute_centroids(object_names: list[str]) -> tuple[list[str], list[list[float]]]:
    """Return (names, centroids) for objects that have accessible coordinates.

    Args:
        object_names: PyMOL object names to process.

    Returns:
        Tuple of ``(names, centroids)`` where each centroid is ``[x, y, z]``.
        Objects without coordinates are silently dropped.
    """
    try:
        import numpy as np
    except ImportError:
        plog(
            _TAG, "install pymolish[numpy] to use cluster_ligands_by_position", "error"
        )
        return [], []

    names: list[str] = []
    centroids: list[list[float]] = []
    for obj in object_names:
        coords: list[list[float]] = []
        try:
            cmd.iterate_state(
                1, obj, "coords.append([x, y, z])", space={"coords": coords}
            )
            if coords:
                centroid = np.mean(coords, axis=0).tolist()
                names.append(obj)
                centroids.append(centroid)
            else:
                plog(_TAG, f"no atoms found in {obj!r}", "warn")
        except Exception as exc:  # noqa: BLE001
            plog(_TAG, f"could not process {obj!r}: {exc}", "warn")
    return names, centroids


def _kmeans(centroids_arr: object, num_groups: int, verbose: bool) -> object:
    """Simple K-means implementation using numpy arrays."""
    import numpy as np  # already guarded at call site

    rng = np.random.default_rng(42)
    lo, hi = centroids_arr.min(axis=0), centroids_arr.max(axis=0)
    centers = rng.uniform(lo, hi, (num_groups, 3))

    for iteration in range(100):
        diff = centroids_arr[:, np.newaxis, :] - centers[np.newaxis, :, :]
        labels = np.argmin((diff**2).sum(axis=2), axis=1)
        new_centers = np.array(
            [
                centroids_arr[labels == i].mean(axis=0)
                if (labels == i).any()
                else centers[i]
                for i in range(num_groups)
            ]
        )
        if np.allclose(centers, new_centers, rtol=1e-4):
            if verbose:
                plog(_TAG, f"k-means converged in {iteration + 1} iteration(s)")
            break
        centers = new_centers
    return labels


def _hierarchical(centroids_arr: object, num_groups: int) -> object:
    """Single-linkage hierarchical clustering."""
    import numpy as np  # already guarded at call site

    n = len(centroids_arr)
    diff = centroids_arr[:, np.newaxis, :] - centroids_arr[np.newaxis, :, :]
    dist_mat = np.sqrt((diff**2).sum(axis=2))
    clusters = [[i] for i in range(n)]

    while len(clusters) > num_groups:
        min_dist = float("inf")
        merge_i, merge_j = 0, 1
        for i in range(len(clusters)):
            for j in range(i + 1, len(clusters)):
                d = min(dist_mat[p1, p2] for p1 in clusters[i] for p2 in clusters[j])
                if d < min_dist:
                    min_dist, merge_i, merge_j = d, i, j
        clusters[merge_i].extend(clusters[merge_j])
        clusters.pop(merge_j)

    labels = np.zeros(n, dtype=int)
    for cid, cluster in enumerate(clusters):
        for pid in cluster:
            labels[pid] = cid
    return labels


def _distance_based(centroids_arr: object, cutoff: float) -> object:
    """Simple distance-cutoff clustering."""
    import numpy as np  # already guarded at call site

    n = len(centroids_arr)
    labels = np.full(n, -1, dtype=int)
    current = 0
    for i in range(n):
        if labels[i] == -1:
            labels[i] = current
            for j in range(i + 1, n):
                if labels[j] == -1:
                    d = float(
                        np.sqrt(np.sum((centroids_arr[i] - centroids_arr[j]) ** 2))
                    )
                    if d <= cutoff:
                        labels[j] = current
            current += 1
    return labels


def cluster_ligands_by_position(
    ligand_group_or_selection: str,
    num_groups: int | str = 2,
    cluster_method: str = "kmeans",
    distance_cutoff: float | str = 10.0,
    group_prefix: str = "ligand_cluster",
    verbose: bool | str | int = True,
) -> dict[str, list[str]]:
    """Cluster ligands by 3-D centroid into new PyMOL groups.

    Resolves *ligand_group_or_selection* to individual objects, computes each
    object's centroid, then clusters using K-means, single-linkage hierarchical,
    or distance-cutoff partitioning.  Each cluster is stored as a new PyMOL
    group named ``{group_prefix}_{n}``.

    Requires **numpy** — install via ``pip install pymolish[numpy]``.

    Args:
        ligand_group_or_selection: PyMOL group or selection containing ligands.
        num_groups: Number of clusters (ignored for ``"distance"`` method).
        cluster_method: ``"kmeans"`` (default), ``"hierarchical"``, or
            ``"distance"``.
        distance_cutoff: Max inter-centroid distance (Å) for the ``"distance"``
            method.
        group_prefix: Prefix for created group names.
        verbose: When truthy, log per-object centroids and cluster assignments.

    Returns:
        Dict mapping each created group name to the list of member object names.
        Returns ``{}`` on error (missing dep, too few ligands, unknown method).

    Examples:
        PyMOL> cluster_ligands_by_position ligands, 3
        PyMOL> cluster_ligands_by_position hetero, 4, hierarchical, 15.0
        PyMOL> cluster_ligands_by_position drug_group, 2, distance, 10.0, my_cl

    Since:
        1.0.0

    See Also:
        cluster_ligands_from_group
    """
    try:
        import numpy as np
    except ImportError:
        plog(
            _TAG, "install pymolish[numpy] to use cluster_ligands_by_position", "error"
        )
        return {}

    verbose = coerce_bool(verbose)
    ligand_group_or_selection = _clean(ligand_group_or_selection)
    num_groups = int(num_groups)
    distance_cutoff = float(distance_cutoff)
    cluster_method = _clean(cluster_method).lower()
    group_prefix = _clean(group_prefix) or "ligand_cluster"

    ligand_objects = _resolve_ligand_objects(ligand_group_or_selection)
    if not ligand_objects:
        try:
            atom_count = cmd.count_atoms(ligand_group_or_selection)
        except Exception:  # noqa: BLE001
            atom_count = 0
        if atom_count == 0:
            plog(_TAG, f"no atoms found in {ligand_group_or_selection!r}", "error")
            return {}

    if verbose:
        plog(
            _TAG,
            f"processing {len(ligand_objects)} ligand object(s) "
            f"(method={cluster_method!r}, n_groups={num_groups})",
        )

    obj_names, centroids = _compute_centroids(ligand_objects)
    if len(centroids) < 2:
        plog(
            _TAG,
            f"need at least 2 ligands to cluster, found {len(centroids)}",
            "error",
        )
        return {}

    if verbose:
        for name, c in zip(obj_names, centroids, strict=True):
            plog(_TAG, f"  {name}: centroid ({c[0]:.2f}, {c[1]:.2f}, {c[2]:.2f})")

    centroids_arr = np.array(centroids)

    if cluster_method == "kmeans":
        labels = _kmeans(centroids_arr, num_groups, verbose)
    elif cluster_method == "hierarchical":
        labels = _hierarchical(centroids_arr, num_groups)
    elif cluster_method == "distance":
        labels = _distance_based(centroids_arr, distance_cutoff)
        num_groups = int(labels.max()) + 1
    else:
        plog(_TAG, f"unknown clustering method {cluster_method!r}", "error")
        return {}

    assignments: dict[str, list[str]] = {}
    for gidx in range(num_groups):
        grp = f"{group_prefix}_{gidx + 1}"
        members = [obj_names[j] for j, lbl in enumerate(labels) if lbl == gidx]
        if not members:
            continue
        try:
            cmd.delete(grp)
        except Exception:  # noqa: BLE001
            pass
        try:
            cmd.group(grp, " ".join(members))
        except Exception as exc:  # noqa: BLE001
            plog(_TAG, f"failed to create group {grp!r}: {exc}", "warn")
            continue
        assignments[grp] = members
        if verbose:
            plog(
                _TAG, f"created group {grp!r} with {len(members)} ligand(s): {members}"
            )

    if verbose:
        plog(
            _TAG,
            f"clustered {len(obj_names)} ligand(s) into {len(assignments)} group(s)",
        )
    return assignments


def cluster_ligands_from_group(
    group_name: str,
    num_groups: int | str = 2,
    cluster_method: str = "kmeans",
    distance_cutoff: float | str = 10.0,
    group_prefix: str = "ligand_cluster",
) -> dict[str, list[str]]:
    """Convenience wrapper: cluster ligands from a named PyMOL group.

    Delegates to :func:`cluster_ligands_by_position` with ``verbose=True``.

    Requires **numpy** — install via ``pip install pymolish[numpy]``.

    Args:
        group_name: Name of PyMOL group containing ligand objects.
        num_groups: Number of clusters to create.
        cluster_method: ``"kmeans"``, ``"hierarchical"``, or ``"distance"``.
        distance_cutoff: Distance cutoff (Å) for the ``"distance"`` method.
        group_prefix: Prefix for new group names.

    Returns:
        Same dict as :func:`cluster_ligands_by_position`.

    Examples:
        PyMOL> cluster_ligands_from_group my_ligands, 2
        PyMOL> cluster_ligands_from_group compounds, 5, hierarchical
        PyMOL> cluster_ligands_from_group drug_group, 3, distance, 12.0

    Since:
        1.0.0

    See Also:
        cluster_ligands_by_position
    """
    try:
        import numpy  # noqa: F401
    except ImportError:
        plog(_TAG, "install pymolish[numpy] to use cluster_ligands_from_group", "error")
        return {}

    return cluster_ligands_by_position(
        group_name,
        num_groups=num_groups,
        cluster_method=cluster_method,
        distance_cutoff=distance_cutoff,
        group_prefix=group_prefix,
        verbose=True,
    )
