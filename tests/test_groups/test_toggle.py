"""Tests for ``pymolish.extensions.groups.toggle``."""

from __future__ import annotations

from pymolish.extensions.groups.toggle import (
    _clean,
    _resolve_targets,
    group_disable,
    group_enable,
    group_status,
    group_toggle,
)

# ------------------------------------------------------------------ helpers


def test_clean_strips_quotes():
    assert _clean('"hello"') == "hello"
    assert _clean("'world'") == "world"
    assert _clean("plain") == "plain"
    assert _clean(42) == 42


def test_resolve_targets_returns_group_members(pymol_cmd):
    pymol_cmd.get_type.return_value = "object:group"
    pymol_cmd.get_object_list.return_value = ["a", "b", "c"]

    result = _resolve_targets("my_group")
    assert result == ["a", "b", "c"]


def test_resolve_targets_falls_back_to_exact_object(pymol_cmd):
    pymol_cmd.get_type.return_value = ""  # not a group
    pymol_cmd.get_names.return_value = ["obj1"]
    pymol_cmd.get_object_list.return_value = ["obj1"]

    result = _resolve_targets("obj1")
    assert result == ["obj1"]


def test_resolve_targets_empty_when_nothing_matches(pymol_cmd):
    pymol_cmd.get_type.return_value = ""
    pymol_cmd.get_names.return_value = []
    pymol_cmd.get_object_list.return_value = []

    result = _resolve_targets("no_such_thing")
    assert result == []


# ------------------------------------------------------------------ group_enable


def test_group_enable_calls_enable_for_each_target(pymol_cmd):
    pymol_cmd.get_type.return_value = "object:group"
    pymol_cmd.get_object_list.return_value = ["a", "b", "c"]

    result = group_enable("my_group")
    assert result == ["a", "b", "c"]
    assert pymol_cmd.enable.call_count == 3


def test_group_enable_every_nth(pymol_cmd):
    pymol_cmd.get_type.return_value = "object:group"
    pymol_cmd.get_object_list.return_value = ["a", "b", "c", "d"]

    result = group_enable("my_group", each=2)
    # sorted targets: a,b,c,d; step=2 -> a, c
    assert result == ["a", "c"]
    assert pymol_cmd.enable.call_count == 2


def test_group_enable_returns_empty_on_no_match(pymol_cmd, capsys):
    pymol_cmd.get_type.return_value = ""
    pymol_cmd.get_names.return_value = []
    pymol_cmd.get_object_list.return_value = []

    result = group_enable("ghost")
    assert result == []
    assert "no objects" in capsys.readouterr().out.lower()


def test_group_enable_handles_cmd_exception(pymol_cmd, capsys):
    pymol_cmd.get_type.return_value = "object:group"
    pymol_cmd.get_object_list.return_value = ["a"]
    pymol_cmd.enable.side_effect = RuntimeError("boom")

    result = group_enable("my_group")
    assert result == []
    assert "failed" in capsys.readouterr().out.lower()


# ------------------------------------------------------------------ group_disable


def test_group_disable_calls_disable_for_each_target(pymol_cmd):
    pymol_cmd.get_type.return_value = "object:group"
    pymol_cmd.get_object_list.return_value = ["x", "y"]

    result = group_disable("my_group")
    assert result == ["x", "y"]
    assert pymol_cmd.disable.call_count == 2


def test_group_disable_every_nth(pymol_cmd):
    pymol_cmd.get_type.return_value = "object:group"
    pymol_cmd.get_object_list.return_value = ["a", "b", "c"]

    result = group_disable("my_group", each=3)
    assert result == ["a"]
    assert pymol_cmd.disable.call_count == 1


# ------------------------------------------------------------------ group_toggle


def test_group_toggle_disables_enabled_objects(pymol_cmd):
    pymol_cmd.get_type.return_value = "object:group"
    pymol_cmd.get_object_list.return_value = ["a", "b"]
    pymol_cmd.get_setting_int.return_value = 1  # both enabled

    result = group_toggle("my_group")
    assert result["disabled"] == ["a", "b"]
    assert result["enabled"] == []


def test_group_toggle_enables_disabled_objects(pymol_cmd):
    pymol_cmd.get_type.return_value = "object:group"
    pymol_cmd.get_object_list.return_value = ["a", "b"]
    pymol_cmd.get_setting_int.return_value = 0  # both disabled

    result = group_toggle("my_group")
    assert result["enabled"] == ["a", "b"]
    assert result["disabled"] == []


def test_group_toggle_returns_empty_on_no_match(pymol_cmd):
    pymol_cmd.get_type.return_value = ""
    pymol_cmd.get_names.return_value = []
    pymol_cmd.get_object_list.return_value = []

    result = group_toggle("ghost")
    assert result == {"enabled": [], "disabled": []}


# ------------------------------------------------------------------ group_status


def test_group_status_separates_enabled_and_disabled(pymol_cmd):
    pymol_cmd.get_type.return_value = "object:group"
    pymol_cmd.get_object_list.return_value = ["a", "b", "c"]

    def _setting(setting, obj):
        return 1 if obj in ("a", "c") else 0

    pymol_cmd.get_setting_int.side_effect = _setting

    result = group_status("my_group")
    assert result["enabled"] == ["a", "c"]
    assert result["disabled"] == ["b"]


def test_group_status_empty_on_no_match(pymol_cmd):
    pymol_cmd.get_type.return_value = ""
    pymol_cmd.get_names.return_value = []
    pymol_cmd.get_object_list.return_value = []

    result = group_status("ghost")
    assert result == {"enabled": [], "disabled": []}
