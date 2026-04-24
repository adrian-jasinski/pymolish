"""Fetch PDB structures by UniProt accession from public APIs.

Heavy dependencies: **requests** (primary / fallback) and **biopython**
(secondary fallback).  Both are gated inside functions.  Install with
``pip install pymolish[biopython]`` which also pulls in ``requests``.
"""

from __future__ import annotations

from pymol import cmd

from pymolish.core.logging import plog
from pymolish.core.validators import coerce_bool

_TAG = "structure.fetch_uniprot"


def _clean(value: str) -> str:
    """Strip one layer of surrounding quotes from PyMOL command arguments."""
    if not isinstance(value, str):
        return value
    return value.strip().strip("'\"")


# ---------------------------------------------------------------------------
# Internal search helpers — each gated on its own import
# ---------------------------------------------------------------------------


def _search_rcsb_graphql(uniprot_id: str, verbose: bool) -> list[str]:
    """Query the RCSB PDB GraphQL endpoint for structures linked to *uniprot_id*.

    Args:
        uniprot_id: UniProt accession string.
        verbose: When truthy, log progress.

    Returns:
        Sorted, deduplicated list of uppercase PDB IDs, or ``[]`` on failure.

    Raises:
        ImportError: When *requests* is not installed.
        RuntimeError: When the HTTP request or GraphQL response is invalid.
    """
    try:
        import requests
    except ImportError:
        plog(_TAG, "install pymolish[biopython] to use fetch_by_uniprot", "error")
        raise

    if verbose:
        plog(_TAG, "trying RCSB PDB GraphQL API…")

    query = """
    query ($uid: String!) {
        polymer_entities(
            where: {
                uniprot: { uniprot_accession: { _eq: $uid } }
            }
        ) { entry { id } }
    }
    """
    resp = requests.post(
        "https://data.rcsb.org/graphql",
        json={"query": query, "variables": {"uid": uniprot_id}},
        headers={"Content-Type": "application/json"},
        timeout=30,
    )
    if resp.status_code != 200:
        raise RuntimeError(f"GraphQL request failed with status {resp.status_code}")
    data = resp.json()
    if "errors" in data:
        raise RuntimeError(f"GraphQL errors: {data['errors']}")
    entities = (data.get("data") or {}).get("polymer_entities") or []
    pdb_ids = sorted({e["entry"]["id"].upper() for e in entities if e.get("entry")})
    if verbose and pdb_ids:
        plog(_TAG, f"GraphQL found {len(pdb_ids)} structure(s)")
    return pdb_ids


def _search_uniprot_rest(uniprot_id: str, verbose: bool) -> list[str]:
    """Query the UniProt REST API cross-references for PDB IDs.

    Args:
        uniprot_id: UniProt accession string.
        verbose: When truthy, log progress.

    Returns:
        List of uppercase PDB IDs, or ``[]`` on failure.

    Raises:
        ImportError: When *requests* is not installed.
        RuntimeError: When the HTTP request fails.
    """
    try:
        import requests
    except ImportError:
        plog(_TAG, "install pymolish[biopython] to use fetch_by_uniprot", "error")
        raise

    if verbose:
        plog(_TAG, "trying UniProt REST API…")

    resp = requests.get(
        f"https://rest.uniprot.org/uniprotkb/{uniprot_id}.json",
        timeout=30,
    )
    if resp.status_code != 200:
        raise RuntimeError(f"UniProt API failed with status {resp.status_code}")
    data = resp.json()
    pdb_ids = [
        ref["id"].upper()
        for ref in data.get("uniProtKBCrossReferences", [])
        if ref.get("database") == "PDB" and ref.get("id")
    ]
    if verbose and pdb_ids:
        plog(_TAG, f"UniProt REST found {len(pdb_ids)} structure(s)")
    return pdb_ids


def _search_biopython(uniprot_id: str, verbose: bool) -> list[str]:
    """Use Biopython's ExPASy/SwissProt interface to list PDB cross-references.

    Args:
        uniprot_id: UniProt accession string.
        verbose: When truthy, log progress.

    Returns:
        List of uppercase PDB IDs, or ``[]`` on failure.

    Raises:
        ImportError: When *biopython* is not installed.
        RuntimeError: On any retrieval error.
    """
    try:
        from Bio import ExPASy, SwissProt
    except ImportError:
        plog(_TAG, "install pymolish[biopython] to use fetch_by_uniprot", "error")
        raise

    if verbose:
        plog(_TAG, "trying Biopython ExPASy fallback…")

    try:
        handle = ExPASy.get_sprot_raw(uniprot_id)
        record = SwissProt.read(handle)
        handle.close()
        pdb_ids = [ref[1].upper() for ref in record.cross_references if ref[0] == "PDB"]
        if verbose and pdb_ids:
            plog(_TAG, f"Biopython found {len(pdb_ids)} structure(s)")
        return pdb_ids
    except Exception as exc:  # noqa: BLE001
        raise RuntimeError(f"Biopython search failed: {exc}") from exc


def _find_pdb_ids(uniprot_id: str, verbose: bool) -> list[str]:
    """Attempt all search strategies and return the first non-empty result.

    Order: RCSB GraphQL → UniProt REST → Biopython.

    Args:
        uniprot_id: UniProt accession string.
        verbose: When truthy, log per-strategy progress.

    Returns:
        List of PDB IDs (may be empty when all strategies fail).
    """
    for searcher in (_search_rcsb_graphql, _search_uniprot_rest, _search_biopython):
        try:
            ids = searcher(uniprot_id, verbose)
            if ids:
                return ids
        except Exception as exc:  # noqa: BLE001
            if verbose:
                plog(_TAG, f"{searcher.__name__} failed: {exc}", "warn")
    return []


# ---------------------------------------------------------------------------
# Public commands
# ---------------------------------------------------------------------------


def fetch_by_uniprot(
    uniprot_id: str,
    max_structures: int | str = 10,
    verbose: bool | str | int = True,
) -> list[str]:
    """Fetch PDB structures for a UniProt accession into PyMOL.

    Tries three search strategies in order (RCSB GraphQL → UniProt REST →
    Biopython) and loads up to *max_structures* PDB entries via
    :pymol:`fetch`.

    Requires **requests** (and optionally **biopython**) — install with
    ``pip install pymolish[biopython]``.

    Args:
        uniprot_id: UniProt accession ID (e.g. ``"P04637"``).
        max_structures: Maximum number of PDB entries to load.
        verbose: When truthy, log per-structure progress.

    Returns:
        List of successfully loaded PDB IDs (uppercase, e.g. ``["1TUP"]``).

    Examples:
        PyMOL> fetch_by_uniprot P04637
        PyMOL> fetch_by_uniprot P38398, 5
        PyMOL> fetch_by_uniprot Q9Y6R4, 3, 0

    Since:
        1.0.0

    See Also:
        list_uniprot_structures
    """
    try:
        import requests  # noqa: F401
    except ImportError:
        plog(_TAG, "install pymolish[biopython] to use fetch_by_uniprot", "error")
        return []

    verbose = coerce_bool(verbose)
    uniprot_id = _clean(uniprot_id).upper()
    max_structures = int(max_structures)

    if not uniprot_id:
        plog(_TAG, "uniprot_id must be non-empty", "error")
        return []

    if verbose:
        plog(_TAG, f"searching PDB structures for UniProt ID {uniprot_id!r}")

    pdb_ids = _find_pdb_ids(uniprot_id, verbose)
    if not pdb_ids:
        plog(_TAG, f"no PDB structures found for {uniprot_id!r}", "error")
        return []

    if len(pdb_ids) > max_structures:
        if verbose:
            plog(
                _TAG,
                f"found {len(pdb_ids)} structures; limiting to {max_structures}",
            )
        pdb_ids = pdb_ids[:max_structures]

    if verbose:
        plog(_TAG, f"fetching {len(pdb_ids)} PDB structure(s)…")

    fetched: list[str] = []
    n = len(pdb_ids)
    for idx, pdb_id in enumerate(pdb_ids, start=1):
        obj_name = f"{uniprot_id}_{pdb_id}"
        try:
            cmd.fetch(pdb_id, obj_name)
            fetched.append(pdb_id)
            if verbose:
                plog(_TAG, f"({idx}/{n}) {pdb_id} → {obj_name}")
        except Exception as exc:  # noqa: BLE001
            plog(_TAG, f"failed to fetch {pdb_id}: {exc}", "warn")

    if fetched:
        if verbose:
            plog(
                _TAG,
                f"fetched {len(fetched)} structure(s) for {uniprot_id}: "
                f"{', '.join(fetched)}",
            )
    else:
        plog(_TAG, f"failed to fetch any structure for {uniprot_id}", "error")

    return fetched


def list_uniprot_structures(
    uniprot_id: str,
    show_details: bool | str | int = True,
) -> list[str]:
    """List PDB structures for a UniProt accession without loading them.

    Queries the same search backends as :func:`fetch_by_uniprot` and prints
    the found PDB IDs with optional per-entry metadata from the RCSB REST API.

    Requires **requests** (and optionally **biopython**) — install with
    ``pip install pymolish[biopython]``.

    Args:
        uniprot_id: UniProt accession ID (e.g. ``"P04637"``).
        show_details: When truthy, fetch RCSB metadata for each entry (title,
            resolution, method).

    Returns:
        List of found PDB IDs (may be empty).

    Examples:
        PyMOL> list_uniprot_structures P04637
        PyMOL> list_uniprot_structures P38398, 1
        PyMOL> list_uniprot_structures Q9Y6R4, 0

    Since:
        1.0.0

    See Also:
        fetch_by_uniprot
    """
    try:
        import requests
    except ImportError:
        plog(
            _TAG, "install pymolish[biopython] to use list_uniprot_structures", "error"
        )
        return []

    show_details = coerce_bool(show_details)
    uniprot_id = _clean(uniprot_id).upper()

    if not uniprot_id:
        plog(_TAG, "uniprot_id must be non-empty", "error")
        return []

    plog(_TAG, f"searching structures for {uniprot_id!r}")
    pdb_ids = _find_pdb_ids(uniprot_id, verbose=False)

    if not pdb_ids:
        plog(_TAG, f"no PDB structures found for {uniprot_id!r}")
        return []

    plog(_TAG, f"found {len(pdb_ids)} PDB structure(s)")

    if show_details:
        for pdb_id in pdb_ids:
            try:
                info_url = f"https://data.rcsb.org/rest/v1/core/entry/{pdb_id}"
                resp = requests.get(info_url, timeout=10)
                if resp.status_code == 200:
                    data = resp.json()
                    title = data.get("struct", {}).get("title", "No title")
                    resolution = data.get("rcsb_entry_info", {}).get(
                        "resolution_combined", "N/A"
                    )
                    method = (data.get("exptl") or [{}])[0].get("method", "Unknown")
                    short_title = title[:60] + ("…" if len(title) > 60 else "")
                    plog(_TAG, f"  {pdb_id}: {short_title} [{method}, {resolution} Å]")
                else:
                    plog(_TAG, f"  {pdb_id}: (details unavailable)")
            except Exception:  # noqa: BLE001
                plog(_TAG, f"  {pdb_id}: (details unavailable)")
    else:
        plog(_TAG, f"  {', '.join(pdb_ids)}")

    return pdb_ids
