"""Tests for ``pymolish.extensions.groups.sort``."""

from __future__ import annotations

from pymolish.extensions.groups.sort import (
    create_sorted_group,
    group_info,
    sort_all_groups,
    sort_group_objects,
)

# ------------------------------------------------------------------ sort_group_objects


def test_sort_group_objects_reorders_members(pymol_cmd):
    pymol_cmd.get_type.return_value = "object:group"
    pymol_cmd.get_object_list.return_value = ["c", "a", "b"]

    result = sort_group_objects("my_group")
    assert result == ["a", "b", "c"]
    # remove then add should have been called via group()
    assert pymol_cmd.group.call_count >= 6  # 3 removes + 3 adds


def test_sort_group_objects_already_sorted(pymol_cmd, capsys):
    pymol_cmd.get_type.return_value = "object:group"
    pymol_cmd.get_object_list.return_value = ["a", "b", "c"]

    result = sort_group_objects("my_group")
    assert result == ["a", "b", "c"]
    assert "already sorted" in capsys.readouterr().out.lower()
    # No group() calls should be made
    pymol_cmd.group.assert_not_called()


def test_sort_group_objects_single_object(pymol_cmd, capsys):
    pymol_cmd.get_type.return_value = "object:group"
    pymol_cmd.get_object_list.return_value = ["only_one"]

    result = sort_group_objects("my_group")
    assert result == ["only_one"]
    pymol_cmd.group.assert_not_called()


def test_sort_group_objects_missing_group(pymol_cmd, capsys):
    pymol_cmd.get_type.return_value = ""
    pymol_cmd.get_object_list.return_value = []
    pymol_cmd.get_names.return_value = []

    result = sort_group_objects("ghost")
    assert result == []
    assert "not found" in capsys.readouterr().out.lower()


def test_sort_group_objects_strips_quotes(pymol_cmd):
    pymol_cmd.get_type.return_value = "object:group"
    pymol_cmd.get_object_list.return_value = ["b", "a"]

    result = sort_group_objects('"my_group"')
    assert result == ["a", "b"]


# ------------------------------------------------------------------ sort_all_groups


def test_sort_all_groups_processes_all(pymol_cmd):
    def _get_names(*args, **kwargs):
        a = args[0] if args else ""
        if a in ("group_objects", "groups"):
            return ["grp1", "grp2"]
        return []

    pymol_cmd.get_names.side_effect = _get_names
    pymol_cmd.get_type.return_value = "object:group"
    pymol_cmd.get_object_list.return_value = ["b", "a"]

    result = sort_all_groups()
    assert "grp1" in result
    assert "grp2" in result


def test_sort_all_groups_empty(pymol_cmd, capsys):
    pymol_cmd.get_names.return_value = []
    result = sort_all_groups()
    assert result == {}
    assert "no groups" in capsys.readouterr().out.lower()


# ------------------------------------------------------------------ group_info


def test_group_info_returns_correct_dict(pymol_cmd):
    pymol_cmd.get_type.return_value = "object:group"
    pymol_cmd.get_object_list.return_value = ["a", "b", "c"]

    info = group_info("my_group")
    assert info["name"] == "my_group"
    assert info["object_count"] == 3
    assert info["objects"] == ["a", "b", "c"]
    assert info["is_sorted"] is True


def test_group_info_reports_unsorted(pymol_cmd):
    pymol_cmd.get_type.return_value = "object:group"
    pymol_cmd.get_object_list.return_value = ["c", "a", "b"]

    info = group_info("my_group")
    assert info["is_sorted"] is False


def test_group_info_missing_group(pymol_cmd, capsys):
    pymol_cmd.get_type.return_value = ""
    pymol_cmd.get_names.return_value = []
    pymol_cmd.get_object_list.return_value = []

    info = group_info("ghost")
    assert info == {}
    assert "not found" in capsys.readouterr().out.lower()


# ------------------------------------------------------------------ create_sorted_group


def test_create_sorted_group_default_name(pymol_cmd):
    pymol_cmd.get_type.return_value = "object:group"
    pymol_cmd.get_object_list.return_value = ["c", "a", "b"]

    result = create_sorted_group("my_group")
    assert result == ["a", "b", "c"]
    # ensure_group calls group() with action='add' for each member
    assert pymol_cmd.group.call_count == 3


def test_create_sorted_group_custom_name(pymol_cmd):
    pymol_cmd.get_type.return_value = "object:group"
    pymol_cmd.get_object_list.return_value = ["b", "a"]

    result = create_sorted_group("src", "dst_sorted")
    assert result == ["a", "b"]
    # Verify new group name used in group() calls
    calls = pymol_cmd.group.call_args_list
    assert any(c.args[0] == "dst_sorted" for c in calls)


def test_create_sorted_group_missing_source(pymol_cmd, capsys):
    pymol_cmd.get_type.return_value = ""
    pymol_cmd.get_names.return_value = []
    pymol_cmd.get_object_list.return_value = []

    result = create_sorted_group("ghost")
    assert result == []
    assert "not found" in capsys.readouterr().out.lower()
