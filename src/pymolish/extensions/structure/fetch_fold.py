"""Fetch predicted structures from AlphaFold DB or ESMFold (stdlib HTTP only)."""

from __future__ import annotations

import hashlib
import json
import re
import urllib.error
import urllib.request

from pymol import cmd

from ...core.cli import clean as _clean
from ...core.logging import plog
from ...core.validators import coerce_bool

_TAG = "structure.fetch_fold"

_ACCESSION_RE = re.compile(
    r"^([OPQ][0-9][A-Z0-9]{3}[0-9]|[A-NR-Z][0-9]([A-Z][A-Z0-9]{2}[0-9]){1,2})$"
)
_AF_MODEL_RE = re.compile(r"^AF-([A-Z0-9]+)-F(\d+)(?:-MODEL_V\d+)?(?:\.PDB|\.CIF)?$")
_AMINO_ACIDS = frozenset("ACDEFGHIKLMNPQRSTVWY")
_ESMFOLD_MAX_LEN = 400

_AFDB_API = "https://alphafold.ebi.ac.uk/api/prediction/{acc}"
_UNIPROT_FASTA = "https://rest.uniprot.org/uniprotkb/{acc}.fasta"
_ESMFOLD_API = "https://api.esmatlas.com/foldSequence/v1/pdb/"


def _http_text(url: str, data: bytes | None = None, timeout: int = 120) -> str:
    """GET *url* (or POST *data*) and return the response body as text.

    Raises:
        urllib.error.URLError: On network or non-2xx HTTP errors.
    """
    req = urllib.request.Request(url, data=data)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode()


def _normalize_sequence(query: str) -> str:
    return "".join(query.split()).upper()


def _parse_af_model_id(query: str) -> tuple[str, int] | None:
    """Return ``(accession, fragment)`` for an AF model ID like ``AF-P04637-F1``."""
    m = _AF_MODEL_RE.match(query.strip().upper())
    return (m.group(1), int(m.group(2))) if m else None


def _is_accession(query: str) -> bool:
    return bool(_ACCESSION_RE.match(query.strip().upper()))


def _is_sequence(query: str) -> bool:
    seq = _normalize_sequence(query)
    return bool(seq) and set(seq) <= _AMINO_ACIDS


def _fetch_alphafold(acc: str, fragment: int = 1) -> str | None:
    """Return the PDB text for *acc* from AlphaFold DB, or ``None`` if absent.

    Long proteins are split into fragments ``AF-<acc>-F1``, ``F2``...; the
    entry whose ``entryId`` matches *fragment* is used, else the first one.
    """
    try:
        entries = json.loads(_http_text(_AFDB_API.format(acc=acc), timeout=30))
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return None
        raise
    if not entries:
        return None
    wanted = f"AF-{acc}-F{fragment}"
    entry = next(
        (e for e in entries if str(e.get("entryId", "")).upper() == wanted),
        entries[0],
    )
    return _http_text(entry["pdbUrl"])


def _uniprot_fasta(acc: str) -> str:
    """Return the bare sequence for *acc* from UniProt REST."""
    body = _http_text(_UNIPROT_FASTA.format(acc=acc), timeout=30)
    return "".join(line for line in body.splitlines() if not line.startswith(">"))


def _fetch_esmfold(seq: str) -> str:
    """Return the PDB text predicted by ESMFold for *seq*."""
    if len(seq) > _ESMFOLD_MAX_LEN:
        plog(
            _TAG,
            f"sequence has {len(seq)} residues; ESMFold API may reject "
            f"inputs longer than {_ESMFOLD_MAX_LEN}",
            "warn",
        )
    return _http_text(_ESMFOLD_API, data=seq.encode())


def fetch_fold(
    query: str,
    name: str = "",
    source: str = "auto",
    color: bool | str | int = True,
    legend: bool | str | int = True,
    verbose: bool | str | int = True,
) -> str | None:
    """Fetch a predicted structure for a UniProt accession or a sequence.

    UniProt accessions and AlphaFold model IDs (``AF-P04637-F1``, optionally
    with ``-model_v4``) are looked up in AlphaFold DB; raw amino-acid
    sequences are folded with the public ESMFold API.  The input type is
    detected automatically.  An accession missing from AlphaFold
    DB falls back to its UniProt sequence folded by ESMFold.  The loaded
    model is colored with the AlphaFold confidence bins and a legend (see
    :func:`color_plddt`).

    Args:
        query: UniProt accession (``P04637``), AlphaFold model ID
            (``AF-P04637-F1``) or one-letter amino-acid sequence.
        name: Object name. Defaults to ``AF_<acc>`` or ``ESM_<hash>``.
        source: ``"auto"`` (detect from *query*), ``"alphafold"`` or
            ``"esmfold"``.
        color: Color by pLDDT after loading. Default: ``True``.
        legend: Draw the pLDDT legend ramp. Default: ``True``.
        verbose: When truthy, log progress. Default: ``True``.

    Returns:
        The loaded object name, or ``None`` on failure.

    Examples:
        PyMOL> fetch_fold P04637
        PyMOL> fetch_fold AF-P04637-F1
        PyMOL> fetch_fold MKTAYIAKQRQISFVKSHFSRQLEERLGLIEVQ
        PyMOL> fetch_fold P04637, p53_model, color=0
        PyMOL> fetch_fold P04637, source=esmfold

    Since:
        0.1.21

    See Also:
        color_plddt, fetch_by_uniprot
    """
    query = _clean(query)
    name = _clean(name)
    source = _clean(source).lower() or "auto"
    color = coerce_bool(color)
    legend = coerce_bool(legend)
    verbose = coerce_bool(verbose)

    if source not in ("auto", "alphafold", "esmfold"):
        plog(_TAG, f"unknown source '{source}' (auto|alphafold|esmfold)", "error")
        return None
    if source == "auto":
        if _is_accession(query) or _parse_af_model_id(query):
            source = "alphafold"
        elif _is_sequence(query):
            source = "esmfold"
        else:
            plog(_TAG, "query is neither a UniProt accession nor a sequence", "error")
            return None

    try:
        pdb_text = None
        if source == "alphafold":
            parsed = _parse_af_model_id(query)
            if parsed:
                acc, fragment = parsed
            elif _is_accession(query):
                acc, fragment = query.strip().upper(), 1
            else:
                plog(_TAG, f"'{query}' is not a UniProt accession or AF ID", "error")
                return None
            name = name or (f"AF_{acc}" if fragment == 1 else f"AF_{acc}_F{fragment}")
            if verbose:
                plog(_TAG, f"fetching AF-{acc}-F{fragment} from AlphaFold DB…")
            pdb_text = _fetch_alphafold(acc, fragment)
            if pdb_text is None:
                plog(_TAG, f"{acc} not in AlphaFold DB - folding with ESMFold", "warn")
                query, source = _uniprot_fasta(acc), "esmfold"
                name = f"ESM_{acc}" if name.startswith(f"AF_{acc}") else name
        if source == "esmfold":
            seq = _normalize_sequence(query)
            if not _is_sequence(seq):
                plog(_TAG, "query is not a valid amino-acid sequence", "error")
                return None
            name = name or f"ESM_{hashlib.sha1(seq.encode()).hexdigest()[:6]}"
            if verbose:
                plog(_TAG, f"folding {len(seq)} residues with ESMFold…")
            pdb_text = _fetch_esmfold(seq)
    except Exception as exc:  # noqa: BLE001
        plog(_TAG, f"download failed: {exc}", "error")
        return None

    cmd.read_pdbstr(pdb_text, name)
    if verbose:
        plog(_TAG, f"loaded '{name}'")

    if color:
        from ..visualization.plddt import color_plddt

        color_plddt(name, legend=legend, verbose=verbose)
    return name
