"""Tests for ``pymolish.extensions.selection.sequence_search``."""

from __future__ import annotations

import sys
from unittest.mock import MagicMock

from pymolish.extensions.selection.sequence_search import search_sequence

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_bio_mock():
    """Return a minimal Biopython mock sufficient for the search_sequence path."""
    bio_mod = MagicMock(name="Bio")

    seq_mod = MagicMock(name="Bio.Seq")
    seq_mod.Seq.side_effect = lambda s: s  # pass-through

    sequtils_mod = MagicMock(name="Bio.SeqUtils")
    sequtils_mod.seq1.side_effect = lambda aa: aa  # identity

    pairwise2_mod = MagicMock(name="Bio.pairwise2")
    # Return one alignment with (_, _, score, start, end)
    pairwise2_mod.align.localms.return_value = [
        (None, None, 16.0, 0, 8),  # score=16/(8*2)=1.0 >= 0.8
    ]

    bio_mod.Seq = seq_mod
    bio_mod.SeqUtils = sequtils_mod
    bio_mod.pairwise2 = pairwise2_mod

    return {
        "Bio": bio_mod,
        "Bio.Seq": seq_mod,
        "Bio.SeqUtils": sequtils_mod,
        "Bio.pairwise2": pairwise2_mod,
    }


# ---------------------------------------------------------------------------
# Graceful degradation — biopython absent
# ---------------------------------------------------------------------------


def test_search_sequence_missing_biopython(pymol_cmd, capsys, monkeypatch):
    """search_sequence returns [] and logs an error when biopython is absent."""
    pymol_cmd.get_object_list.return_value = ["prot"]

    for key in list(sys.modules.keys()):
        if key == "Bio" or key.startswith("Bio."):
            monkeypatch.delitem(sys.modules, key, raising=False)

    monkeypatch.setitem(sys.modules, "Bio", None)
    monkeypatch.setitem(sys.modules, "Bio.pairwise2", None)
    monkeypatch.setitem(sys.modules, "Bio.Seq", None)
    monkeypatch.setitem(sys.modules, "Bio.SeqUtils", None)

    result = search_sequence("ACDEF")
    assert result == []

    out = capsys.readouterr().out
    assert "biopython" in out.lower()
    assert "error" in out.lower()


# ---------------------------------------------------------------------------
# Validation errors
# ---------------------------------------------------------------------------


def test_search_sequence_empty_sequence_returns_empty(pymol_cmd, capsys):
    result = search_sequence("")
    assert result == []
    out = capsys.readouterr().out
    assert "non-empty" in out.lower()


def test_search_sequence_no_objects_loaded(pymol_cmd, capsys, monkeypatch):
    """Returns [] with an error when no structures are loaded."""
    pymol_cmd.get_object_list.return_value = []

    bio_mocks = _make_bio_mock()
    for key, val in bio_mocks.items():
        monkeypatch.setitem(sys.modules, key, val)

    result = search_sequence("ACDEF")
    assert result == []
    out = capsys.readouterr().out
    assert "no structures" in out.lower()


# ---------------------------------------------------------------------------
# Happy path (biopython mocked)
# ---------------------------------------------------------------------------


def test_search_sequence_creates_selection(pymol_cmd, capsys, monkeypatch):
    """search_sequence calls cmd.select for each alignment hit."""
    pymol_cmd.get_object_list.return_value = ["prot1"]

    bio_mocks = _make_bio_mock()
    # seq1 returns each character unchanged, get_fastastr returns fasta-like text
    pymol_cmd.get_fastastr.return_value = ">prot1\nACDEFGHIK"
    bio_mocks["Bio.SeqUtils"].seq1.side_effect = lambda aa: aa

    for key, val in bio_mocks.items():
        monkeypatch.setitem(sys.modules, key, val)

    result = search_sequence("ACDEFGHIK", "myhit", 0.8)

    assert len(result) == 1
    assert result[0] == "myhit_prot1_0_8"
    pymol_cmd.select.assert_called_once_with("myhit_prot1_0_8", "prot1 and resi 0-8")

    out = capsys.readouterr().out
    assert "match" in out.lower()


def test_search_sequence_default_selection_name(pymol_cmd, monkeypatch):
    """When selection_name is omitted the base name is seq_<first5chars>."""
    pymol_cmd.get_object_list.return_value = ["mol"]
    pymol_cmd.get_fastastr.return_value = ">mol\nACDEF"

    bio_mocks = _make_bio_mock()
    bio_mocks["Bio.SeqUtils"].seq1.side_effect = lambda aa: aa
    for key, val in bio_mocks.items():
        monkeypatch.setitem(sys.modules, key, val)

    result = search_sequence("ACDEF")
    assert len(result) == 1
    assert result[0].startswith("seq_ACDEF")


def test_search_sequence_no_hits_above_threshold(pymol_cmd, capsys, monkeypatch):
    """Returns [] and warns when all alignments are below min_score."""
    pymol_cmd.get_object_list.return_value = ["prot"]
    pymol_cmd.get_fastastr.return_value = ">prot\nXXXXX"

    bio_mocks = _make_bio_mock()
    bio_mocks["Bio.SeqUtils"].seq1.side_effect = lambda aa: aa
    # Score 0 / (5*2) = 0.0, well below 0.8
    bio_mocks["Bio.pairwise2"].align.localms.return_value = [
        (None, None, 0.0, 0, 5),
    ]
    for key, val in bio_mocks.items():
        monkeypatch.setitem(sys.modules, key, val)

    result = search_sequence("ACDEF", min_score=0.8)
    assert result == []
    out = capsys.readouterr().out
    assert "no matches" in out.lower()


def test_search_sequence_skips_object_on_fasta_error(pymol_cmd, capsys, monkeypatch):
    """Objects that raise on get_fastastr are skipped with a warning."""
    pymol_cmd.get_object_list.return_value = ["bad_obj", "good_obj"]
    pymol_cmd.get_fastastr.side_effect = [
        RuntimeError("fasta error"),
        ">good_obj\nACDEF",
    ]

    bio_mocks = _make_bio_mock()
    bio_mocks["Bio.SeqUtils"].seq1.side_effect = lambda aa: aa
    for key, val in bio_mocks.items():
        monkeypatch.setitem(sys.modules, key, val)

    result = search_sequence("ACDEF", "hit", 0.8)

    out = capsys.readouterr().out
    assert "bad_obj" in out
    assert len(result) == 1
    assert "good_obj" in result[0]


def test_search_sequence_invalid_min_score(pymol_cmd, capsys, monkeypatch):
    """Returns [] and logs error when min_score cannot be coerced to float."""
    pymol_cmd.get_object_list.return_value = ["prot"]
    bio_mocks = _make_bio_mock()
    for key, val in bio_mocks.items():
        monkeypatch.setitem(sys.modules, key, val)

    result = search_sequence("ACDEF", min_score="not_a_number")
    assert result == []
    out = capsys.readouterr().out
    assert "min_score" in out.lower()
