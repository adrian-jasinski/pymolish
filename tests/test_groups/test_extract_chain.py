"""Tests for ``pymolish.extensions.groups.extract_chain``."""

from __future__ import annotations

from pymolish.extensions.groups.extract_chain import (
    extract_chain_from_group,
    extract_chains_from_group,
)

# ------------------------------------------------------------------ helpers


def _setup_group(pymol_cmd, members, atom_count=10):
    """Configure mocks for a group with *members* and non-zero atom counts."""
    pymol_cmd.get_type.return_value = "object:group"
    pymol_cmd.get_object_list.return_value = members
    pymol_cmd.get_names.return_value = members
    pymol_cmd.count_atoms.return_value = atom_count


# ---------------------------------------------------------- extract_chain_from_group


def test_extract_chain_from_group_creates_objects(pymol_cmd):
    _setup_group(pymol_cmd, ["prot1", "prot2"])

    result = extract_chain_from_group("my_group", "A")
    assert result == ["chain_extract_prot1_A", "chain_extract_prot2_A"]
    assert pymol_cmd.create.call_count == 2


def test_extract_chain_from_group_custom_prefix(pymol_cmd):
    _setup_group(pymol_cmd, ["x"])

    result = extract_chain_from_group("my_group", "B", prefix="myprefix")
    assert result == ["myprefix_x_B"]


def test_extract_chain_from_group_replaces_existing(pymol_cmd):
    # chain_extract_prot1_A already loaded; group has only "prot1".
    pymol_cmd.get_type.return_value = "object:group"

    def _get_names(*args, **kwargs):
        if kwargs.get("selection") == "my_group":
            return ["prot1"]  # group members
        return ["prot1", "chain_extract_prot1_A"]  # all objects

    pymol_cmd.get_names.side_effect = _get_names
    pymol_cmd.get_object_list.return_value = ["prot1"]
    pymol_cmd.count_atoms.return_value = 5

    result = extract_chain_from_group("my_group", "A")
    assert result == ["chain_extract_prot1_A"]
    pymol_cmd.delete.assert_called()


def test_extract_chain_from_group_skips_empty_chain(pymol_cmd, capsys):
    _setup_group(pymol_cmd, ["prot1"], atom_count=0)

    result = extract_chain_from_group("my_group", "Z")
    assert result == []
    assert "no atoms" in capsys.readouterr().out.lower()


def test_extract_chain_from_group_empty_chain_arg(pymol_cmd, capsys):
    result = extract_chain_from_group("my_group", "")
    assert result == []
    assert "non-empty" in capsys.readouterr().out.lower()


def test_extract_chain_from_group_no_match(pymol_cmd, capsys):
    pymol_cmd.get_type.return_value = ""
    pymol_cmd.get_object_list.return_value = []
    pymol_cmd.get_names.return_value = []
    pymol_cmd.count_atoms.return_value = 0

    result = extract_chain_from_group("ghost", "A")
    assert result == []
    assert "no objects" in capsys.readouterr().out.lower()


def test_extract_chain_no_group_add(pymol_cmd):
    _setup_group(pymol_cmd, ["prot1"])

    result = extract_chain_from_group("my_group", "A", add_to_group=False)
    assert result == ["chain_extract_prot1_A"]
    # group() should NOT be called for adding to a target group
    group_add_calls = [c for c in pymol_cmd.group.call_args_list if "add" in str(c)]
    assert not group_add_calls


# --------------------------------------------------------- extract_chains_from_group


def test_extract_chains_from_group_multiple_chains(pymol_cmd):
    _setup_group(pymol_cmd, ["prot1"])

    result = extract_chains_from_group("my_group", "A,B")
    assert "A" in result
    assert "B" in result
    assert result["A"] == ["chain_extract_prot1_A"]
    assert result["B"] == ["chain_extract_prot1_B"]


def test_extract_chains_from_group_empty_chains(pymol_cmd, capsys):
    result = extract_chains_from_group("my_group", "")
    assert result == {}
    assert "non-empty" in capsys.readouterr().out.lower()


def test_extract_chains_from_group_partial_success(pymol_cmd):
    _setup_group(pymol_cmd, ["prot1"])

    def _count_atoms(sel):
        return 5 if "chain A" in sel else 0

    pymol_cmd.count_atoms.side_effect = _count_atoms

    result = extract_chains_from_group("my_group", "A,Z")
    assert result["A"] == ["chain_extract_prot1_A"]
    assert result["Z"] == []
