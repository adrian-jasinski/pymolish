"""Tests for ``pymolish.extensions.structure.cluster_ligands``."""

from __future__ import annotations

import sys

import pytest

from pymolish.extensions.structure.cluster_ligands import (
    _resolve_ligand_objects,
    cluster_ligands_by_position,
    cluster_ligands_from_group,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _block_numpy(monkeypatch):
    """Patch sys.modules so that ``import numpy`` raises ImportError."""
    monkeypatch.setitem(sys.modules, "numpy", None)


# ---------------------------------------------------------------------------
# _resolve_ligand_objects
# ---------------------------------------------------------------------------


def test_resolve_uses_get_object_list(pymol_cmd):
    pymol_cmd.get_object_list.return_value = ["lig_a", "lig_b"]
    result = _resolve_ligand_objects("my_group")
    assert result == ["lig_a", "lig_b"]


def test_resolve_falls_back_to_intersection(pymol_cmd):
    pymol_cmd.get_object_list.side_effect = [Exception("no group"), ["x", "y"]]
    pymol_cmd.count_atoms.return_value = 1
    result = _resolve_ligand_objects("resn LIG")
    assert set(result) == {"x", "y"}


def test_resolve_returns_empty_when_nothing(pymol_cmd):
    pymol_cmd.get_object_list.return_value = []
    pymol_cmd.count_atoms.return_value = 0
    result = _resolve_ligand_objects("ghost")
    assert result == []


# ---------------------------------------------------------------------------
# Graceful degradation: numpy missing
# ---------------------------------------------------------------------------


def test_cluster_ligands_by_position_no_numpy(pymol_cmd, monkeypatch, capsys):
    _block_numpy(monkeypatch)
    result = cluster_ligands_by_position("my_group", 2)
    assert result == {}
    out = capsys.readouterr().out
    assert "pymolish[numpy]" in out


def test_cluster_ligands_from_group_no_numpy(pymol_cmd, monkeypatch, capsys):
    _block_numpy(monkeypatch)
    result = cluster_ligands_from_group("my_group", 2)
    assert result == {}
    out = capsys.readouterr().out
    assert "pymolish[numpy]" in out


# ---------------------------------------------------------------------------
# Happy-path tests (skipped when numpy is absent)
# ---------------------------------------------------------------------------


numpy = pytest.importorskip("numpy", reason="numpy not installed")


def _make_iterate_state(coords_per_obj):
    """Return a side-effect callable for cmd.iterate_state.

    ``coords_per_obj``: list of coord lists, one per call.
    """
    call_count = [0]

    def side_effect(state, obj, expr, space=None):
        idx = call_count[0]
        if idx < len(coords_per_obj):
            space["coords"].extend(coords_per_obj[idx])
        call_count[0] += 1

    return side_effect


def test_cluster_ligands_kmeans_happy(pymol_cmd):
    """K-means clustering with 4 ligands → 2 groups, each containing 2 objects."""
    pymol_cmd.get_object_list.return_value = ["l1", "l2", "l3", "l4"]
    # Two spatial clusters: l1/l2 near (0,0,0) and l3/l4 near (100,100,100)
    coords = [
        [[0.0, 0.0, 0.0]],
        [[1.0, 1.0, 1.0]],
        [[100.0, 100.0, 100.0]],
        [[101.0, 101.0, 101.0]],
    ]
    pymol_cmd.iterate_state.side_effect = _make_iterate_state(coords)
    pymol_cmd.count_atoms.return_value = 5

    result = cluster_ligands_by_position("my_group", 2, "kmeans", verbose=False)
    assert len(result) == 2
    all_members = [m for ms in result.values() for m in ms]
    assert sorted(all_members) == ["l1", "l2", "l3", "l4"]


def test_cluster_ligands_hierarchical_happy(pymol_cmd):
    pymol_cmd.get_object_list.return_value = ["a", "b", "c"]
    coords = [
        [[0.0, 0.0, 0.0]],
        [[1.0, 0.0, 0.0]],
        [[50.0, 0.0, 0.0]],
    ]
    pymol_cmd.iterate_state.side_effect = _make_iterate_state(coords)
    pymol_cmd.count_atoms.return_value = 5

    result = cluster_ligands_by_position("grp", 2, "hierarchical", verbose=False)
    assert len(result) == 2
    members = sorted(m for ms in result.values() for m in ms)
    assert members == ["a", "b", "c"]


def test_cluster_ligands_distance_happy(pymol_cmd):
    pymol_cmd.get_object_list.return_value = ["x", "y", "z"]
    coords = [
        [[0.0, 0.0, 0.0]],
        [[5.0, 0.0, 0.0]],  # within 10 Å of x
        [[100.0, 0.0, 0.0]],  # far from others
    ]
    pymol_cmd.iterate_state.side_effect = _make_iterate_state(coords)
    pymol_cmd.count_atoms.return_value = 5

    result = cluster_ligands_by_position("grp", 2, "distance", 10.0, verbose=False)
    # x and y should be in the same cluster; z in its own
    assert len(result) == 2


def test_cluster_ligands_unknown_method_returns_empty(pymol_cmd, capsys):
    pymol_cmd.get_object_list.return_value = ["a", "b"]
    coords = [[[0.0, 0.0, 0.0]], [[1.0, 0.0, 0.0]]]
    pymol_cmd.iterate_state.side_effect = _make_iterate_state(coords)
    pymol_cmd.count_atoms.return_value = 5

    result = cluster_ligands_by_position("grp", 2, "bogus_method", verbose=False)
    assert result == {}
    assert "unknown" in capsys.readouterr().out.lower()


def test_cluster_ligands_too_few_objects(pymol_cmd, capsys):
    # Only 1 ligand — cannot cluster
    pymol_cmd.get_object_list.return_value = ["only_one"]
    coords = [[[0.0, 0.0, 0.0]]]
    pymol_cmd.iterate_state.side_effect = _make_iterate_state(coords)
    pymol_cmd.count_atoms.return_value = 5

    result = cluster_ligands_by_position("grp", 2, verbose=False)
    assert result == {}
    assert "at least 2" in capsys.readouterr().out.lower()


def test_cluster_ligands_from_group_delegates(pymol_cmd):
    pymol_cmd.get_object_list.return_value = ["p", "q"]
    coords = [[[0.0, 0.0, 0.0]], [[100.0, 0.0, 0.0]]]
    pymol_cmd.iterate_state.side_effect = _make_iterate_state(coords)
    pymol_cmd.count_atoms.return_value = 5

    result = cluster_ligands_from_group("grp", 2)
    assert len(result) > 0
