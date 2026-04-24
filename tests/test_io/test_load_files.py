"""Tests for ``pymolish.extensions.io.load_files``."""

from __future__ import annotations

from pymolish.extensions.io.load_files import (
    _normalize_exclude_subdirs,
    _strip_quotes,
    list_loadable_files,
    load_files,
    load_recursive,
)


def _make_tree(root, files):
    """Create ``files`` (list of relative paths) under ``root`` as empty files."""
    for rel in files:
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.touch()


def test_strip_quotes_handles_single_and_double():
    assert _strip_quotes('"foo"') == "foo"
    assert _strip_quotes("'foo'") == "foo"
    assert _strip_quotes("foo") == "foo"
    assert _strip_quotes(None) is None
    assert _strip_quotes(123) == 123


def test_normalize_exclude_subdirs_accepts_string_list_and_none():
    assert _normalize_exclude_subdirs(None) == []
    assert _normalize_exclude_subdirs("") == []
    assert _normalize_exclude_subdirs("traj") == ["traj"]
    assert _normalize_exclude_subdirs("traj, cache") == ["traj", "cache"]
    assert _normalize_exclude_subdirs(["a", "", " b "]) == ["a", "b"]


def test_load_files_flat_directory(pymol_cmd, tmp_path):
    _make_tree(tmp_path, ["a.pdb", "b.pdb", "c.cif"])
    pymol_cmd.get_names.return_value = []

    result = load_files(str(tmp_path), "pdb", verbose=False)
    assert sorted(result) == ["a", "b"]
    assert pymol_cmd.load.call_count == 2


def test_load_files_applies_name_filter(pymol_cmd, tmp_path):
    _make_tree(tmp_path, ["model_1.pdb", "model_2.pdb", "ligand.pdb"])
    pymol_cmd.get_names.return_value = []

    result = load_files(str(tmp_path), "pdb", name_filter="model_*", verbose=False)
    assert sorted(result) == ["model_1", "model_2"]


def test_load_files_missing_directory(pymol_cmd, tmp_path, capsys):
    result = load_files(str(tmp_path / "nope"), "pdb", verbose=False)
    assert result == []
    assert "not an existing directory" in capsys.readouterr().out


def test_load_files_empty_directory(pymol_cmd, tmp_path):
    result = load_files(str(tmp_path), "pdb", verbose=False)
    assert result == []
    assert pymol_cmd.load.call_count == 0


def test_load_files_resolves_name_collisions(pymol_cmd, tmp_path):
    _make_tree(tmp_path, ["a.pdb", "b.pdb"])
    pymol_cmd.get_names.return_value = ["a"]

    result = load_files(str(tmp_path), "pdb", verbose=False)
    # "a" already taken, so unique_name returns "a_2"
    assert "a_2" in result
    assert "b" in result


def test_load_files_creates_group_when_specified(pymol_cmd, tmp_path):
    _make_tree(tmp_path, ["a.pdb", "b.pdb"])
    pymol_cmd.get_names.return_value = []

    load_files(str(tmp_path), "pdb", group_name="my_grp", verbose=False)
    # ensure_group should trigger cmd.group calls with action="add" per member
    group_calls = [
        call
        for call in pymol_cmd.group.call_args_list
        if call.args and call.args[0] == "my_grp"
    ]
    assert len(group_calls) == 2


def test_load_recursive_walks_subdirectories(pymol_cmd, tmp_path):
    _make_tree(tmp_path, ["top.pdb", "sub/nested.pdb", "sub/deep/inner.pdb"])
    pymol_cmd.get_names.return_value = []

    result = load_recursive(str(tmp_path), "pdb", max_depth=5, verbose=False)
    assert set(result) == {"top", "sub_nested", "sub_deep_inner"}


def test_load_files_honours_exclude_subdirs(pymol_cmd, tmp_path):
    _make_tree(tmp_path, ["a.pdb", "traj/old.pdb"])
    pymol_cmd.get_names.return_value = []

    result = load_files(
        str(tmp_path), "pdb", recursive=True, exclude_subdirs="traj", verbose=False
    )
    assert result == ["a"]


def test_list_loadable_files_reports_and_returns_paths(pymol_cmd, tmp_path, capsys):
    _make_tree(tmp_path, ["a.pdb", "b.pdb"])
    paths = list_loadable_files(str(tmp_path), "pdb")
    assert len(paths) == 2
    out = capsys.readouterr().out
    assert "a.pdb" in out and "b.pdb" in out


def test_load_files_invalid_suffix(pymol_cmd, tmp_path, capsys):
    result = load_files(str(tmp_path), "", verbose=False)
    assert result == []
    assert "suffix" in capsys.readouterr().out.lower()
