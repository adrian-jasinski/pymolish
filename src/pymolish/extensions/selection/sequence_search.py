"""Search for amino acid sequences in loaded PyMOL structures using alignment."""

from __future__ import annotations

from pymol import cmd

from pymolish.core.logging import plog

_TAG = "selection.sequence_search"


def _clean(value: str) -> str:
    """Strip one layer of surrounding quotes from PyMOL command arguments."""
    if not isinstance(value, str):
        return value
    return value.strip().strip("'\"")


def _get_sequence_from_selection(selection: str) -> str:
    """Get one-letter amino acid sequence from a PyMOL selection.

    Args:
        selection: PyMOL selection string.

    Returns:
        One-letter amino acid sequence string.
    """
    try:
        from Bio.SeqUtils import seq1
    except ImportError as exc:
        raise ImportError(
            "biopython is required; install with: pip install pymolish[biopython]"
        ) from exc

    raw = cmd.get_fastastr(selection)
    return "".join(seq1(aa) for aa in raw.split("\n")[1:])


def _find_sequence_matches(
    query_sequence: str,
    target_sequence: str,
    min_score: float = 0.8,
) -> list[tuple[int, int, float]]:
    """Find local alignment matches between query and target sequences.

    Args:
        query_sequence: Query sequence to search for.
        target_sequence: Target sequence to search in.
        min_score: Minimum normalized alignment score (0–1) to accept.

    Returns:
        List of ``(start, end, score)`` tuples for each accepted match.
    """
    try:
        from Bio import pairwise2
        from Bio.Seq import Seq
    except ImportError as exc:
        raise ImportError(
            "biopython is required; install with: pip install pymolish[biopython]"
        ) from exc

    query = Seq(query_sequence)
    target = Seq(target_sequence)

    alignments = pairwise2.align.localms(
        query,
        target,
        2,  # match score
        -1,  # mismatch penalty
        -0.5,  # gap open penalty
        -0.1,  # gap extend penalty
    )

    matches: list[tuple[int, int, float]] = []
    for alignment in alignments:
        score = alignment[2] / (len(query) * 2)  # normalize
        if score >= min_score:
            matches.append((alignment[3], alignment[4], score))
    return matches


def search_sequence(
    sequence: str,
    selection_name: str = "",
    min_score: float = 0.8,
) -> list[str]:
    """Search for an amino acid sequence in all loaded structures.

    Uses local pairwise alignment (Smith-Waterman via Biopython) to find
    regions matching ``sequence`` in every loaded PyMOL object. Hits are
    materialized as PyMOL selections named
    ``<selection_name>_<object>_<start>_<end>``.

    Requires Biopython (``pip install pymolish[biopython]``).

    Args:
        sequence: One-letter amino acid sequence to search for.
        selection_name: Base name for created selections. Defaults to
            ``seq_<first-5-chars>``.
        min_score: Minimum normalized alignment score in [0, 1].
            Defaults to ``0.8``.

    Returns:
        List of selection names created (empty list on failure or no hits).

    Examples:
        PyMOL> search_sequence MVLSPADKTNVKAA
        PyMOL> search_sequence ACDEFGH, mysel, 0.7
        PyMOL> search_sequence PEPTIDE, hit, 0.9

    Since:
        1.0.0

    See Also:
        pymolish_list, pymolish_search
    """
    sequence = _clean(sequence)

    if not sequence:
        plog(_TAG, "sequence must be non-empty", "error")
        return []

    # Validate biopython is present early so the error is clear.
    try:
        from Bio import pairwise2  # noqa: F401
        from Bio.Seq import Seq  # noqa: F401
        from Bio.SeqUtils import seq1  # noqa: F401
    except ImportError:
        plog(
            _TAG,
            "biopython is required for search_sequence; "
            "install with: pip install pymolish[biopython]",
            "error",
        )
        return []

    sel_base = _clean(selection_name) if selection_name else f"seq_{sequence[:5]}"

    try:
        min_score = float(min_score)
    except (TypeError, ValueError):
        plog(_TAG, f"min_score must be a number, got {min_score!r}", "error")
        return []

    objects = cmd.get_object_list()
    if not objects:
        plog(_TAG, "no structures loaded in PyMOL", "error")
        return []

    created: list[str] = []

    for obj in objects:
        try:
            obj_sequence = _get_sequence_from_selection(obj)
        except Exception as exc:  # noqa: BLE001
            plog(_TAG, f"could not get sequence from {obj!r}: {exc}", "warn")
            continue

        try:
            matches = _find_sequence_matches(sequence, obj_sequence, min_score)
        except Exception as exc:  # noqa: BLE001
            plog(_TAG, f"alignment failed for {obj!r}: {exc}", "warn")
            continue

        for start, end, score in matches:
            sel_name = f"{sel_base}_{obj}_{start}_{end}"
            cmd.select(sel_name, f"{obj} and resi {start}-{end}")
            plog(_TAG, f"match in {obj!r} residues {start}-{end} score={score:.2f}")
            created.append(sel_name)

    if not created:
        plog(_TAG, "no matches found above score threshold", "warn")

    return created
