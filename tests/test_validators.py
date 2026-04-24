"""Smoke tests for ``pymolish.core.validators``."""

from __future__ import annotations

from pathlib import Path

import pytest

from pymolish.core.validators import (
    coerce_bool,
    validate_directory,
    validate_group_exists,
    validate_object_exists,
    validate_selection,
    validate_suffix,
)


def test_validate_directory_returns_resolved_path(tmp_path):
    result = validate_directory(str(tmp_path))
    assert result == tmp_path.resolve()


def test_validate_directory_rejects_missing(tmp_path):
    missing = tmp_path / "nope"
    with pytest.raises(NotADirectoryError):
        validate_directory(str(missing))


def test_validate_suffix_normalizes_dots_and_case():
    assert validate_suffix(".PDB") == "pdb"
    assert validate_suffix("cif") == "cif"
    with pytest.raises(ValueError):
        validate_suffix("")


def test_validate_group_exists(pymol_cmd):
    pymol_cmd.get_type.return_value = "object:group"
    assert validate_group_exists("my_group") is True
    pymol_cmd.get_type.return_value = "object:molecule"
    assert validate_group_exists("not_a_group") is False
    assert validate_group_exists("") is False


def test_validate_object_exists(pymol_cmd):
    pymol_cmd.get_object_list.return_value = ["a", "b"]
    assert validate_object_exists("a") is True
    assert validate_object_exists("c") is False


def test_validate_selection_uses_count_atoms(pymol_cmd):
    pymol_cmd.count_atoms.return_value = 5
    assert validate_selection("chain A") is True
    pymol_cmd.count_atoms.return_value = 0
    assert validate_selection("chain A") is False


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (True, True),
        (False, False),
        (1, True),
        (0, False),
        ("1", True),
        ("0", False),
        ("yes", True),
        ("on", True),
        ("no", False),
        ("", False),
    ],
)
def test_coerce_bool(value, expected):
    assert coerce_bool(value) is expected


def test_validate_directory_expands_home(tmp_path, monkeypatch):
    # Ensure the expansion path works even when the directory exists via ~
    fake_home = tmp_path / "home"
    fake_home.mkdir()
    monkeypatch.setenv("HOME", str(fake_home))
    result = validate_directory("~")
    assert isinstance(result, Path)
    assert result.is_dir()
