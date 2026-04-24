"""Tests for ``pymolish.extensions.groups.merge``."""

from __future__ import annotations

from pymolish.extensions.groups.merge import (
    list_merged_objects,
    merge_to_group,
    merge_to_objects,
)

# ------------------------------------------------------------------ merge_to_group


def test_merge_to_group_creates_merged_objects(pymol_cmd):
    # "lig" is the struct; group "my_group" has members ["a", "b"].
    # Distinguish get_names("objects", selection=...) from get_names("objects").
    pymol_cmd.get_type.return_value = "object:group"

    def _get_names(*args, **kwargs):
        if kwargs.get("selection") == "my_group":
            return ["a", "b"]
        return ["lig", "a", "b"]  # all objects

    pymol_cmd.get_names.side_effect = _get_names
    pymol_cmd.get_object_list.return_value = ["a", "b"]

    result = merge_to_group("my_group", "lig")
    assert result == ["a_with_lig", "b_with_lig"]
    assert pymol_cmd.select.call_count == 2
    assert pymol_cmd.create.call_count == 2
    assert pymol_cmd.delete.call_count == 2


def test_merge_to_group_skips_existing_merged(pymol_cmd, capsys):
    pymol_cmd.get_type.return_value = "object:group"

    def _get_names(*args, **kwargs):
        if kwargs.get("selection") == "my_group":
            return ["a"]
        return ["lig", "a", "a_with_lig"]

    pymol_cmd.get_names.side_effect = _get_names
    pymol_cmd.get_object_list.return_value = ["a"]

    result = merge_to_group("my_group", "lig")
    assert result == []
    assert "already exists" in capsys.readouterr().out.lower()


def test_merge_to_group_missing_struct(pymol_cmd, capsys):
    pymol_cmd.get_names.return_value = []
    pymol_cmd.get_object_list.return_value = []
    pymol_cmd.get_type.return_value = ""

    result = merge_to_group("my_group", "ghost_lig")
    assert result == []
    assert "not found" in capsys.readouterr().out.lower()


def test_merge_to_group_missing_group(pymol_cmd, capsys):
    # "lig" exists but "ghost_group" is not a group and has no objects.
    # get_names returns [] always so get_group_objects fails all strategies.
    pymol_cmd.get_type.return_value = ""
    pymol_cmd.get_names.return_value = []
    pymol_cmd.get_object_list.side_effect = lambda *args: (
        ["lig"] if not args else []  # bare call → all objects; with arg → empty
    )

    result = merge_to_group("ghost_group", "lig")
    assert result == []
    assert "not found" in capsys.readouterr().out.lower()


def test_merge_to_group_default_new_group_name(pymol_cmd):
    pymol_cmd.get_type.return_value = "object:group"

    def _get_names(*args, **kwargs):
        if kwargs.get("selection") == "my_group":
            return ["a"]
        return ["lig", "a"]

    pymol_cmd.get_names.side_effect = _get_names
    pymol_cmd.get_object_list.return_value = ["a"]

    merge_to_group("my_group", "lig")
    group_calls = pymol_cmd.group.call_args_list
    assert any(c.args[0] == "merge_to_lig" for c in group_calls)


# ------------------------------------------------------------------ merge_to_objects


def test_merge_to_objects_basic(pymol_cmd):
    pymol_cmd.get_names.return_value = ["lig", "obj1", "obj2"]
    pymol_cmd.get_object_list.return_value = ["lig", "obj1", "obj2"]
    pymol_cmd.get_type.return_value = ""

    result = merge_to_objects("obj1,obj2", "lig")
    assert result == ["obj1_with_lig", "obj2_with_lig"]


def test_merge_to_objects_skips_nonexistent(pymol_cmd, capsys):
    pymol_cmd.get_names.return_value = ["lig", "obj1"]
    pymol_cmd.get_object_list.return_value = ["lig", "obj1"]
    pymol_cmd.get_type.return_value = ""

    result = merge_to_objects("obj1,ghost", "lig")
    assert result == ["obj1_with_lig"]
    assert "not found" in capsys.readouterr().out.lower()


def test_merge_to_objects_empty_names(pymol_cmd, capsys):
    pymol_cmd.get_names.return_value = ["lig"]
    pymol_cmd.get_object_list.return_value = ["lig"]
    pymol_cmd.get_type.return_value = ""

    result = merge_to_objects("", "lig")
    assert result == []
    assert "non-empty" in capsys.readouterr().out.lower()


def test_merge_to_objects_missing_struct(pymol_cmd, capsys):
    pymol_cmd.get_names.return_value = []
    pymol_cmd.get_object_list.return_value = []
    pymol_cmd.get_type.return_value = ""

    result = merge_to_objects("obj1", "ghost_lig")
    assert result == []
    assert "not found" in capsys.readouterr().out.lower()


# ------------------------------------------------------------------ list_merged_objects


def test_list_merged_objects_finds_matches(pymol_cmd):
    pymol_cmd.get_names.return_value = [
        "a_with_lig",
        "b_with_lig",
        "a",
        "b",
        "lig",
    ]

    result = list_merged_objects("lig")
    assert result == ["a_with_lig", "b_with_lig"]


def test_list_merged_objects_no_matches(pymol_cmd, capsys):
    pymol_cmd.get_names.return_value = ["a", "b"]

    result = list_merged_objects("lig")
    assert result == []
    assert "no merged" in capsys.readouterr().out.lower()


def test_list_merged_objects_empty_struct_name(pymol_cmd, capsys):
    result = list_merged_objects("")
    assert result == []
    assert "non-empty" in capsys.readouterr().out.lower()
