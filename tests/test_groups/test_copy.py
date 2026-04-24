"""Tests for ``pymolish.extensions.groups.copy``."""

from __future__ import annotations

from pymolish.extensions.groups.copy import (
    copy_group,
    copy_group_objects,
    list_group_copies,
)

# ------------------------------------------------------------------ copy_group


def test_copy_group_copies_members_with_suffix(pymol_cmd):
    # Group "my_group" has members ["a", "b"]; no copies exist yet
    pymol_cmd.get_type.return_value = "object:group"
    pymol_cmd.get_object_list.return_value = ["a", "b"]
    pymol_cmd.get_names.return_value = ["a", "b"]

    result = copy_group("my_group")
    assert result == ["a_cpy", "b_cpy"]
    assert pymol_cmd.copy.call_count == 2


def test_copy_group_custom_suffix(pymol_cmd):
    pymol_cmd.get_type.return_value = "object:group"
    pymol_cmd.get_object_list.return_value = ["x"]
    pymol_cmd.get_names.return_value = ["x"]

    result = copy_group("g", new_group_name="g_bak", object_suffix="_bak")
    assert result == ["x_bak"]
    pymol_cmd.copy.assert_called_once_with("x_bak", "x")


def test_copy_group_skips_existing_dest(pymol_cmd, capsys):
    # Group has one member "a"; "a_cpy" already exists.
    # Use side_effect on get_names to distinguish group-member queries
    # (which carry a selection kwarg) from all-object queries.
    pymol_cmd.get_type.return_value = "object:group"

    def _get_names(*args, **kwargs):
        if kwargs.get("selection") == "my_group":
            return ["a"]  # group has only "a"
        return ["a", "a_cpy"]  # all objects include the copy

    pymol_cmd.get_names.side_effect = _get_names
    # get_object_list fallback also returns group members
    pymol_cmd.get_object_list.return_value = ["a"]

    result = copy_group("my_group")
    assert result == []
    assert "already exists" in capsys.readouterr().out.lower()
    pymol_cmd.copy.assert_not_called()


def test_copy_group_missing_group(pymol_cmd, capsys):
    pymol_cmd.get_type.return_value = ""
    pymol_cmd.get_names.return_value = []
    pymol_cmd.get_object_list.return_value = []

    result = copy_group("ghost")
    assert result == []
    assert "not found" in capsys.readouterr().out.lower()


def test_copy_group_default_new_name(pymol_cmd):
    pymol_cmd.get_type.return_value = "object:group"
    pymol_cmd.get_object_list.return_value = ["a"]
    pymol_cmd.get_names.return_value = ["a"]

    copy_group("original")
    calls = pymol_cmd.group.call_args_list
    # new group name should be "original_cpy"
    assert any(c.args[0] == "original_cpy" for c in calls)


# ------------------------------------------------------------------ copy_group_objects


def test_copy_group_objects_basic(pymol_cmd):
    # obj1, obj2 exist; obj1_cpy, obj2_cpy do not
    pymol_cmd.get_names.return_value = ["obj1", "obj2"]
    pymol_cmd.get_object_list.return_value = ["obj1", "obj2"]

    result = copy_group_objects("obj1,obj2", "backup_group")
    assert result == ["obj1_cpy", "obj2_cpy"]
    assert pymol_cmd.copy.call_count == 2


def test_copy_group_objects_skips_nonexistent(pymol_cmd, capsys):
    pymol_cmd.get_names.return_value = ["real"]
    pymol_cmd.get_object_list.return_value = ["real"]

    result = copy_group_objects("real,ghost", "grp")
    assert result == ["real_cpy"]
    assert "not found" in capsys.readouterr().out.lower()


def test_copy_group_objects_empty_names(pymol_cmd, capsys):
    result = copy_group_objects("", "grp")
    assert result == []
    assert "non-empty" in capsys.readouterr().out.lower()


def test_copy_group_objects_all_nonexistent(pymol_cmd, capsys):
    pymol_cmd.get_names.return_value = []
    pymol_cmd.get_object_list.return_value = []

    result = copy_group_objects("ghost1,ghost2", "grp")
    assert result == []
    assert "no valid" in capsys.readouterr().out.lower()


# ------------------------------------------------------------------ list_group_copies


def test_list_group_copies_finds_copies(pymol_cmd):
    pymol_cmd.get_type.return_value = "object:group"
    pymol_cmd.get_object_list.return_value = ["a", "b"]
    # All objects in the scene
    pymol_cmd.get_names.return_value = ["a", "a_cpy", "a_bak", "b", "c"]

    result = list_group_copies("my_group")
    assert "a" in result
    assert sorted(result["a"]) == ["a_bak", "a_cpy"]
    assert "b" not in result  # no copies of b


def test_list_group_copies_no_copies(pymol_cmd, capsys):
    pymol_cmd.get_type.return_value = "object:group"
    pymol_cmd.get_object_list.return_value = ["a", "b"]
    pymol_cmd.get_names.return_value = ["a", "b"]

    result = list_group_copies("my_group")
    assert result == {}
    assert "no copies" in capsys.readouterr().out.lower()


def test_list_group_copies_missing_group(pymol_cmd, capsys):
    pymol_cmd.get_type.return_value = ""
    pymol_cmd.get_names.return_value = []
    pymol_cmd.get_object_list.return_value = []

    result = list_group_copies("ghost")
    assert result == {}
