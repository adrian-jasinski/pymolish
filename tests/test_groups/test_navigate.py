"""Tests for ``pymolish.extensions.groups.navigate``."""

from __future__ import annotations

from pymolish.extensions.groups.navigate import (
    _get_group_members,
    _resolve_group,
    group_next,
    group_previous,
)

# ------------------------------------------------------------------ helpers


def test_get_group_members_uses_get_object_list(pymol_cmd):
    pymol_cmd.get_object_list.return_value = ["a", "b"]
    result = _get_group_members("my_group")
    assert result == ["a", "b"]


def test_get_group_members_falls_back_to_group_utils(pymol_cmd):
    # get_object_list raises; group_utils path (get_names -> get_object_list)
    pymol_cmd.get_object_list.side_effect = RuntimeError("unavailable")
    result = _get_group_members("my_group")
    assert result == []


def test_resolve_group_validates_named_group(pymol_cmd):
    pymol_cmd.get_object_list.return_value = ["a", "b"]
    result = _resolve_group("my_group")
    assert result == "my_group"


def test_resolve_group_returns_none_when_empty(pymol_cmd, capsys):
    pymol_cmd.get_object_list.return_value = []
    result = _resolve_group("empty_group")
    assert result is None
    assert "not found" in capsys.readouterr().out.lower()


def test_resolve_group_auto_detects_single_group(pymol_cmd):
    # No explicit name; one group available
    pymol_cmd.get_names.side_effect = lambda *args, **kwargs: (
        ["my_group"]
        if args and args[0] in ("group_objects", "groups")
        else ["my_group"]
    )
    pymol_cmd.get_object_list.return_value = ["a"]
    # get_type → is_group
    pymol_cmd.get_type.return_value = "object:group"

    result = _resolve_group("")
    assert result == "my_group"


# ------------------------------------------------------------------ group_next


def test_group_next_enables_first_when_none_enabled(pymol_cmd):
    pymol_cmd.get_object_list.return_value = ["a", "b", "c"]
    # No objects enabled
    pymol_cmd.get_names.side_effect = lambda *args, **kwargs: (
        [] if kwargs.get("enabled_only") else ["a", "b", "c"]
    )

    result = group_next("my_group")
    assert result == "a"
    pymol_cmd.enable.assert_called()


def test_group_next_advances_from_current(pymol_cmd):
    pymol_cmd.get_object_list.return_value = ["a", "b", "c"]

    def _get_names(*args, **kwargs):
        if kwargs.get("enabled_only"):
            return ["b"]
        return ["a", "b", "c"]

    pymol_cmd.get_names.side_effect = _get_names

    result = group_next("my_group")
    assert result == "c"
    pymol_cmd.enable.assert_called()
    pymol_cmd.disable.assert_called()


def test_group_next_wraps_around(pymol_cmd):
    pymol_cmd.get_object_list.return_value = ["a", "b", "c"]

    def _get_names(*args, **kwargs):
        if kwargs.get("enabled_only"):
            return ["c"]
        return ["a", "b", "c"]

    pymol_cmd.get_names.side_effect = _get_names

    result = group_next("my_group")
    assert result == "a"


def test_group_next_warns_on_multiple_enabled(pymol_cmd, capsys):
    pymol_cmd.get_object_list.return_value = ["a", "b", "c"]

    def _get_names(*args, **kwargs):
        if kwargs.get("enabled_only"):
            return ["a", "b"]
        return ["a", "b", "c"]

    pymol_cmd.get_names.side_effect = _get_names

    result = group_next("my_group")
    assert result is None
    assert "multiple" in capsys.readouterr().out.lower()


def test_group_next_returns_none_when_group_missing(pymol_cmd, capsys):
    pymol_cmd.get_object_list.return_value = []
    result = group_next("ghost")
    assert result is None


# ------------------------------------------------------------------ group_previous


def test_group_previous_enables_last_when_none_enabled(pymol_cmd):
    pymol_cmd.get_object_list.return_value = ["a", "b", "c"]
    pymol_cmd.get_names.side_effect = lambda *args, **kwargs: (
        [] if kwargs.get("enabled_only") else ["a", "b", "c"]
    )

    result = group_previous("my_group")
    assert result == "c"


def test_group_previous_moves_backward(pymol_cmd):
    pymol_cmd.get_object_list.return_value = ["a", "b", "c"]

    def _get_names(*args, **kwargs):
        if kwargs.get("enabled_only"):
            return ["b"]
        return ["a", "b", "c"]

    pymol_cmd.get_names.side_effect = _get_names

    result = group_previous("my_group")
    assert result == "a"
