"""Tests for ``pymolish.extensions.io.export_group``."""

from __future__ import annotations

from pymolish.extensions.io.export_group import (
    export_by_pattern,
    export_group,
    export_objects,
)


def test_export_group_unknown_group_returns_empty(pymol_cmd, tmp_path, capsys):
    # Multi-API get_group_objects returns None when the group isn't found
    pymol_cmd.get_names.return_value = []
    pymol_cmd.get_object_list.return_value = []

    result = export_group("missing", str(tmp_path))
    assert result == []
    out = capsys.readouterr().out
    assert "not found" in out


def test_export_group_invalid_format(pymol_cmd, tmp_path, capsys):
    result = export_group("grp", str(tmp_path), format_type="xyz")
    assert result == []
    assert "invalid format" in capsys.readouterr().out.lower()


def test_export_group_writes_files(pymol_cmd, tmp_path):
    # First lookup returns group members; is_object lookups use get_all_objects
    pymol_cmd.get_names.side_effect = lambda *a, **kw: ["a", "b"]
    pymol_cmd.get_object_list.return_value = ["a", "b"]

    out_dir = tmp_path / "out"
    result = export_group("grp", str(out_dir), format_type="cif")
    assert len(result) == 2
    # pymol_cmd.save should have been called for both members
    saved_names = {c.args[1] for c in pymol_cmd.save.call_args_list}
    assert saved_names == {"a", "b"}


def test_export_group_respects_overwrite(pymol_cmd, tmp_path):
    pymol_cmd.get_names.side_effect = lambda *a, **kw: ["a"]
    pymol_cmd.get_object_list.return_value = ["a"]

    # Pre-create the target file to simulate a previous export
    out_dir = tmp_path / "out"
    out_dir.mkdir()
    (out_dir / "a.cif").write_text("existing")

    # overwrite disabled -> should skip
    result = export_group("grp", str(out_dir), format_type="cif", overwrite=False)
    assert result == []

    # overwrite enabled -> should proceed
    result = export_group("grp", str(out_dir), format_type="cif", overwrite=True)
    assert len(result) == 1


def test_export_objects_from_csv_string(pymol_cmd, tmp_path):
    pymol_cmd.get_names.return_value = ["a", "b", "c"]

    out_dir = tmp_path / "out"
    result = export_objects("a, b", str(out_dir), format_type="pdb")
    assert len(result) == 2


def test_export_objects_skips_missing(pymol_cmd, tmp_path, capsys):
    pymol_cmd.get_names.return_value = ["a"]
    out_dir = tmp_path / "out"
    result = export_objects(["a", "missing"], str(out_dir))
    assert len(result) == 1
    assert "missing" in capsys.readouterr().out


def test_export_by_pattern_dispatches_to_export_objects(pymol_cmd, tmp_path):
    pymol_cmd.get_names.return_value = ["protein_1", "protein_2", "ligand"]

    out_dir = tmp_path / "out"
    result = export_by_pattern("protein_*", str(out_dir), format_type="pdb")
    assert len(result) == 2


def test_export_by_pattern_no_match(pymol_cmd, tmp_path, capsys):
    pymol_cmd.get_names.return_value = ["ligand"]
    result = export_by_pattern("protein_*", str(tmp_path))
    assert result == []
    assert "no objects matched" in capsys.readouterr().out
