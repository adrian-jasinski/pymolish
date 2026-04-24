"""Tests for ``pymolish.extensions.structure.multialign``."""

from __future__ import annotations

from pymolish.extensions.structure.multialign import (
    _clean,
    _get_objects_from_group_or_selection,
    list_objects_with_prefix,
    multialign,
)

# ---------------------------------------------------------------------------
# _clean
# ---------------------------------------------------------------------------


def test_clean_strips_single_quotes():
    assert _clean("'hello'") == "hello"


def test_clean_strips_double_quotes():
    assert _clean('"world"') == "world"


def test_clean_leaves_bare_strings():
    assert _clean("protein") == "protein"


def test_clean_non_str_passthrough():
    assert _clean(42) == 42  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# _get_objects_from_group_or_selection
# ---------------------------------------------------------------------------


def test_get_objects_uses_get_names(pymol_cmd):
    pymol_cmd.get_names.return_value = ["obj_a", "obj_b"]
    result = _get_objects_from_group_or_selection("my_group")
    assert result == ["obj_a", "obj_b"]


def test_get_objects_falls_back_to_atom_count(pymol_cmd):
    # Strategy 1 returns empty; strategy 2 finds objects via atom-count intersection.
    # get_names first call (strategy 1) returns [] so we proceed to strategy 2.
    # In strategy 2 get_names("objects") is called again and returns the candidates.
    pymol_cmd.get_names.side_effect = [
        [],  # strategy 1: empty group membership
        ["x", "y"],  # strategy 2: all objects
    ]
    pymol_cmd.count_atoms.return_value = 1  # every object matches the selection
    result = _get_objects_from_group_or_selection("resn LIG")
    assert set(result) >= {"x", "y"}


def test_get_objects_wildcard(pymol_cmd):
    # Strategy 1: empty list (group lookup found nothing).
    # Strategy 2: atom-count intersection yields nothing (count_atoms=0).
    # Strategy 3: wildcard match — get_names("objects") returns the full list.
    pymol_cmd.get_names.side_effect = [
        [],  # strategy 1: no group members
        ["prot_a", "prot_b", "lig"],  # strategy 2: all objects (no matches, count=0)
        ["prot_a", "prot_b", "lig"],  # strategy 3: all objects for fnmatch
    ]
    pymol_cmd.count_atoms.return_value = 0  # intersection gives nothing
    result = _get_objects_from_group_or_selection("prot_*")
    assert result == ["prot_a", "prot_b"]


def test_get_objects_returns_empty_when_nothing_matches(pymol_cmd):
    pymol_cmd.get_names.return_value = []
    pymol_cmd.count_atoms.return_value = 0
    result = _get_objects_from_group_or_selection("ghost")
    assert result == []


# ---------------------------------------------------------------------------
# multialign
# ---------------------------------------------------------------------------


def test_multialign_empty_target_returns_empty(pymol_cmd, capsys):
    result = multialign("grp", "", verbose=False)
    assert result == {}
    assert "non-empty" in capsys.readouterr().out


def test_multialign_target_not_found_returns_empty(pymol_cmd, capsys):
    pymol_cmd.count_atoms.return_value = 0
    result = multialign("grp", "missing", verbose=False)
    assert result == {}
    assert "not found" in capsys.readouterr().out


def test_multialign_no_objects_returns_empty(pymol_cmd, capsys):
    # target has atoms; group is empty
    def count_side(sel):
        return 5 if sel == "ref" else 0

    pymol_cmd.count_atoms.side_effect = count_side
    pymol_cmd.get_names.return_value = []
    result = multialign("empty_grp", "ref", verbose=False)
    assert result == {}


def test_multialign_skips_target_object(pymol_cmd):
    # objects include the target itself
    pymol_cmd.count_atoms.return_value = 5
    pymol_cmd.get_names.return_value = ["ref", "mobile"]
    pymol_cmd.align.return_value = (0.5, 10, 10, 10, 10, None, 0)
    result = multialign("my_group", "ref", verbose=False)
    # "ref" == target, should be skipped; "mobile" should be aligned
    assert "mobile" in result
    assert "ref" not in result


def test_multialign_returns_rmsd_dict(pymol_cmd):
    pymol_cmd.count_atoms.return_value = 10
    pymol_cmd.get_names.return_value = ["a", "b"]
    pymol_cmd.align.side_effect = [
        (1.0, 10, 10, 10, 10, None, 0),
        (2.5, 10, 10, 10, 10, None, 0),
    ]
    result = multialign("grp", "target", verbose=False)
    assert result == {"a": 1.0, "b": 2.5}


def test_multialign_handles_failed_alignment(pymol_cmd, capsys):
    pymol_cmd.count_atoms.return_value = 5
    pymol_cmd.get_names.return_value = ["good", "bad"]
    pymol_cmd.align.side_effect = [
        (0.3, 10, 10, 10, 10, None, 0),
        Exception("alignment error"),
    ]
    result = multialign("grp", "ref", verbose=True)
    assert "good" in result
    assert "bad" not in result
    out = capsys.readouterr().out
    assert "failed" in out.lower()


def test_multialign_prints_statistics(pymol_cmd, capsys):
    pymol_cmd.count_atoms.return_value = 5
    pymol_cmd.get_names.return_value = ["a", "b", "c"]
    pymol_cmd.align.side_effect = [
        (1.0, 5, 5, 5, 5, None, 0),
        (2.0, 5, 5, 5, 5, None, 0),
        (3.0, 5, 5, 5, 5, None, 0),
    ]
    multialign("grp", "ref", verbose=True)
    out = capsys.readouterr().out
    assert "summary" in out.lower()
    assert "mean" in out.lower()


# ---------------------------------------------------------------------------
# list_objects_with_prefix
# ---------------------------------------------------------------------------


def test_list_objects_with_prefix_filters(pymol_cmd, capsys):
    pymol_cmd.get_names.return_value = ["prot_a", "prot_b", "lig_x"]
    result = list_objects_with_prefix("prot_")
    assert result == ["prot_a", "prot_b"]
    assert "prot_a" in capsys.readouterr().out


def test_list_objects_with_empty_prefix_returns_all(pymol_cmd, capsys):
    pymol_cmd.get_names.return_value = ["a", "b", "c"]
    result = list_objects_with_prefix()
    assert set(result) == {"a", "b", "c"}


def test_list_objects_no_match(pymol_cmd):
    pymol_cmd.get_names.return_value = ["foo", "bar"]
    result = list_objects_with_prefix("xyz_")
    assert result == []
