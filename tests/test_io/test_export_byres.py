"""Tests for ``pymolish.extensions.io.export_byres``."""

from __future__ import annotations

import csv

from pymolish.extensions.io.export_byres import export_byres_to_csv


def _populate(space, rows):
    """Helper for iterate side effect — inject residue tuples."""
    residues = space["residues"]
    for row in rows:
        residues.add(row)


def test_export_byres_writes_sorted_unique_rows(pymol_cmd, tmp_path):
    pymol_cmd.count_atoms.return_value = 10

    def iterate_side_effect(selection, expr, space=None):
        _populate(space, [("A", "ALA", "1"), ("A", "GLY", "2"), ("A", "ALA", "1")])

    pymol_cmd.iterate.side_effect = iterate_side_effect

    outfile = tmp_path / "residues.csv"
    count = export_byres_to_csv("protein", str(outfile))
    assert count == 2  # dedup

    with outfile.open(newline="") as fh:
        rows = list(csv.reader(fh))
    assert rows[0] == ["chain", "resname", "resid"]
    assert rows[1:] == [["A", "ALA", "1"], ["A", "GLY", "2"]]


def test_export_byres_creates_parent_directory(pymol_cmd, tmp_path):
    pymol_cmd.count_atoms.return_value = 1

    def iterate_side_effect(selection, expr, space=None):
        _populate(space, [("A", "ALA", "1")])

    pymol_cmd.iterate.side_effect = iterate_side_effect

    outfile = tmp_path / "nested" / "out.csv"
    count = export_byres_to_csv("protein", str(outfile))
    assert count == 1
    assert outfile.exists()


def test_export_byres_empty_selection_returns_zero(pymol_cmd, tmp_path, capsys):
    pymol_cmd.count_atoms.return_value = 0
    outfile = tmp_path / "out.csv"
    assert export_byres_to_csv("chain Z", str(outfile)) == 0
    assert not outfile.exists()
    assert "no atoms" in capsys.readouterr().out.lower()


def test_export_byres_rejects_empty_args(pymol_cmd, tmp_path, capsys):
    assert export_byres_to_csv("", str(tmp_path / "x.csv")) == 0
    assert export_byres_to_csv("protein", "") == 0
    out = capsys.readouterr().out
    assert "selection" in out and "outfile" in out
