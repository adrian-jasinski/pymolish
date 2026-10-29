"""Fetch PDB structures by UniProt accession from public APIs.

HTTP uses the stdlib only.  **biopython** is an optional last-resort
fallback (ExPASy); when it is missing that step is skipped.
"""

from __future__ import annotations

import json
import urllib.request

from pymol import cmd

from ...core.cli import clean as _clean
from ...core.logging import plog
from ...core.validators import coerce_bool

_TAG = "structure.fetch_uniprot"


# ---------------------------------------------------------------------------
# Internal search helpers
# ---------------------------------------------------------------------------


def _http_json(url: str, payload: dict | None = None, timeout: int = 30) -> dict:
    """GET *url* (or POST *payload* as JSON) and return the decoded JSON body.

    Args:
        url: Endpoint URL.
        payload: When given, sent as a JSON POST body.
        timeout: Socket timeout in seconds.

    Returns:
        Decoded JSON response.

    Raises:
        urllib.error.URLError: On network or non-2xx HTTP errors.
    """
    data = None if payload is None else json.dumps(payload).encode()
    req = urllib.request.Request(
        url, data=data, headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.load(resp)


def _search_rcsb_graphql(uniprot_id: str, verbose: bool) -> list[str]:
    """Query the RCSB PDB GraphQL endpoint for structures linked to *uniprot_id*.

    Args:
        uniprot_id: UniProt accession string.
        verbose: When truthy, log progress.

    Returns:
        Sorted, deduplicated list of uppercase PDB IDs, or ``[]`` on failure.

    Raises:
        urllib.error.URLError: When the HTTP request fails.
        RuntimeError: When the GraphQL response reports errors.
    """
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
    data = _http_json(
        "https://data.rcsb.org/graphql",
        {"query": query, "variables": {"uid": uniprot_id}},
    )
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
        urllib.error.URLError: When the HTTP request fails.
    """
    if verbose:
        plog(_TAG, "trying UniProt REST API…")

    data = _http_json(f"https://rest.uniprot.org/uniprotkb/{uniprot_id}.json")
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

    Optional: when Biopython is not installed, the step is skipped with an
    informational note instead of failing.

    Returns:
        List of uppercase PDB IDs, or ``[]`` when Biopython is missing.

    Raises:
        RuntimeError: On any retrieval error.
    """
    try:
        from Bio import ExPASy, SwissProt
    except ImportError:
        plog(
            _TAG,
            "biopython not installed - skipping ExPASy fallback "
            "(optional: pip install 'pymolish[biopython]')",
        )
        return []

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

    No extra packages required; **biopython** (``pymolish[biopython]``) adds
    an optional ExPASy fallback that is skipped when absent.

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

    No extra packages required; **biopython** (``pymolish[biopython]``) adds
    an optional ExPASy fallback that is skipped when absent.

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
                data = _http_json(
                    f"https://data.rcsb.org/rest/v1/core/entry/{pdb_id}", timeout=10
                )
                title = data.get("struct", {}).get("title", "No title")
                resolution = data.get("rcsb_entry_info", {}).get(
                    "resolution_combined", "N/A"
                )
                method = (data.get("exptl") or [{}])[0].get("method", "Unknown")
                short_title = title[:60] + ("…" if len(title) > 60 else "")
                plog(_TAG, f"  {pdb_id}: {short_title} [{method}, {resolution} Å]")
            except Exception:  # noqa: BLE001
                plog(_TAG, f"  {pdb_id}: (details unavailable)")
    else:
        plog(_TAG, f"  {', '.join(pdb_ids)}")

    return pdb_ids


def _find_ligands(pdb_ids: list[str], min_weight: float) -> dict[str, str]:
    """Map ligand chemical-component IDs to names for the given PDB entries.

    Args:
        pdb_ids: PDB entry IDs to inspect.
        min_weight: Skip components lighter than this (ions, water-like additives).

    Returns:
        Dict ``{comp_id: name}`` of unique small molecules.

    Raises:
        urllib.error.URLError: When the HTTP request fails.
        RuntimeError: When the GraphQL response reports errors.
    """
    query = """
    query ($ids: [String!]!) {
        entries(entry_ids: $ids) {
            nonpolymer_entities {
                nonpolymer_comp { chem_comp { id name formula_weight } }
            }
        }
    }
    """
    ligands: dict[str, str] = {}
    for i in range(0, len(pdb_ids), 200):  # ponytail: fixed batch size
        data = _http_json(
            "https://data.rcsb.org/graphql",
            {"query": query, "variables": {"ids": pdb_ids[i : i + 200]}},
        )
        if "errors" in data:
            raise RuntimeError(f"GraphQL errors: {data['errors']}")
        for entry in (data.get("data") or {}).get("entries") or []:
            for ent in (entry or {}).get("nonpolymer_entities") or []:
                comp = ent["nonpolymer_comp"]["chem_comp"]
                if (comp.get("formula_weight") or 0) >= min_weight:
                    ligands[comp["id"]] = comp.get("name") or ""
    return ligands


def fetch_uniprot_ligands(
    uniprot_id: str,
    min_weight: float | str = 100.0,
    max_ligands: int | str = 0,
    verbose: bool | str | int = True,
) -> list[str]:
    """Load every distinct ligand (small molecule) seen in a protein's PDB entries.

    Finds all PDB entries for the UniProt accession, collects their non-polymer
    components from RCSB, and loads each unique ligand's ideal 3D model (SDF)
    as object ``<uniprot_id>_<comp_id>``. Ions and small additives (glycerol,
    sulfate, ...) are dropped via *min_weight*. Ligands are loaded standalone,
    not in their bound pose; use :func:`fetch_by_uniprot` for that.

    No extra packages required.

    Args:
        uniprot_id: UniProt accession ID (e.g. ``"P00918"``).
        min_weight: Minimum molecular weight (Da) for a component to count.
        max_ligands: Maximum number of ligands to load (0 = no limit).
        verbose: When truthy, log per-ligand progress.

    Returns:
        List of loaded ligand component IDs (e.g. ``["AZM", "BEZ"]``).

    Examples:
        PyMOL> fetch_uniprot_ligands P00918
        PyMOL> fetch_uniprot_ligands P00918, 150
        PyMOL> fetch_uniprot_ligands P00918, 100, 20, 0

    Since:
        1.0.0

    See Also:
        fetch_by_uniprot, list_uniprot_structures
    """
    verbose = coerce_bool(verbose)
    uniprot_id = _clean(uniprot_id).upper()
    min_weight = float(min_weight)
    max_ligands = int(max_ligands)

    if not uniprot_id:
        plog(_TAG, "uniprot_id must be non-empty", "error")
        return []

    pdb_ids = _find_pdb_ids(uniprot_id, verbose)
    if not pdb_ids:
        plog(_TAG, f"no PDB structures found for {uniprot_id!r}", "error")
        return []

    try:
        ligands = _find_ligands(pdb_ids, min_weight)
    except Exception as exc:  # noqa: BLE001
        plog(_TAG, f"ligand lookup failed: {exc}", "error")
        return []
    if not ligands:
        plog(_TAG, f"no ligands found in {len(pdb_ids)} entries of {uniprot_id}")
        return []

    comp_ids = sorted(ligands)
    if max_ligands > 0:
        comp_ids = comp_ids[:max_ligands]
    if verbose:
        plog(
            _TAG,
            f"{len(ligands)} ligand(s) in {len(pdb_ids)} entries; "
            f"loading {len(comp_ids)}",
        )

    loaded: list[str] = []
    for idx, comp_id in enumerate(comp_ids, start=1):
        obj_name = f"{uniprot_id}_{comp_id}"
        try:
            url = f"https://files.rcsb.org/ligands/download/{comp_id}_ideal.sdf"
            with urllib.request.urlopen(url, timeout=30) as resp:
                cmd.read_molstr(resp.read().decode(), obj_name)
            loaded.append(comp_id)
            if verbose:
                plog(
                    _TAG,
                    f"({idx}/{len(comp_ids)}) {comp_id} "
                    f"({ligands[comp_id]}) → {obj_name}",
                )
        except Exception as exc:  # noqa: BLE001
            plog(_TAG, f"failed to fetch ligand {comp_id}: {exc}", "warn")

    plog(_TAG, f"loaded {len(loaded)} ligand(s) for {uniprot_id}")
    return loaded
