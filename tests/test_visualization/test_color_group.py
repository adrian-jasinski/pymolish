"""Tests for ``pymolish.extensions.visualization.color_group``."""

from __future__ import annotations

from pymolish.extensions.visualization.color_group import (
    _resolve_targets,
    color_group_with_gradient,
    color_group_with_palette,
)

# ---------------------------------------------------------------------------
# _resolve_targets helper
# ---------------------------------------------------------------------------


def test_resolve_targets_uses_get_object_list(pymol_cmd):
    pymol_cmd.get_object_list.return_value = ["obj_a", "obj_b"]
    result = _resolve_targets("my_group")
    assert result == ["obj_a", "obj_b"]


def test_resolve_targets_falls_back_to_atom_count_scan(pymol_cmd):
    # First call returns empty; fall back to scan
    pymol_cmd.get_object_list.side_effect = [[], ["obj_a", "obj_b"]]
    pymol_cmd.count_atoms.return_value = 5
    result = _resolve_targets("all")
    assert set(result) == {"obj_a", "obj_b"}


def test_resolve_targets_empty_when_no_objects(pymol_cmd):
    pymol_cmd.get_object_list.return_value = []
    pymol_cmd.count_atoms.return_value = 0
    result = _resolve_targets("nothing")
    assert result == []


# ---------------------------------------------------------------------------
# color_group_with_palette
# ---------------------------------------------------------------------------


def test_color_group_with_palette_colors_each_object(pymol_cmd):
    pymol_cmd.get_object_list.return_value = ["a", "b", "c"]
    result = color_group_with_palette("my_group", "pastels", verbose=False)
    assert set(result.keys()) == {"a", "b", "c"}
    assert pymol_cmd.color.call_count == 3


def test_color_group_with_palette_cycles_colors(pymol_cmd):
    # 26 objects, palette has 25 colors — 26th wraps back to index 0
    objects = [f"obj_{i}" for i in range(26)]
    pymol_cmd.get_object_list.return_value = objects
    result = color_group_with_palette("grp", "pastels", verbose=False)
    # obj_0 and obj_25 share the same color (cycle)
    assert result["obj_0"] == result["obj_25"]


def test_color_group_with_palette_unknown_palette_returns_empty(pymol_cmd, capsys):
    result = color_group_with_palette("grp", "no_palette", verbose=False)
    assert result == {}
    assert "unknown palette" in capsys.readouterr().out.lower()


def test_color_group_with_palette_no_objects_returns_empty(pymol_cmd, capsys):
    pymol_cmd.get_object_list.return_value = []
    pymol_cmd.count_atoms.return_value = 0
    result = color_group_with_palette("empty_grp", "pastels", verbose=False)
    assert result == {}
    assert "no objects" in capsys.readouterr().out.lower()


def test_color_group_with_palette_start_index_offset(pymol_cmd):
    pymol_cmd.get_object_list.return_value = ["x"]
    result = color_group_with_palette("g", "neon", start_index=5, verbose=False)
    assert result["x"] == "neon_06"


def test_color_group_with_palette_auto_register_calls_set_color(pymol_cmd):
    pymol_cmd.get_object_list.return_value = ["x"]
    color_group_with_palette("g", "pastels", auto_register=True, verbose=False)
    assert pymol_cmd.set_color.call_count == 25


def test_color_group_with_palette_no_auto_register_skips_set_color(pymol_cmd):
    pymol_cmd.get_object_list.return_value = ["x"]
    color_group_with_palette("g", "pastels", auto_register=False, verbose=False)
    pymol_cmd.set_color.assert_not_called()


def test_color_group_with_palette_verbose_logs(pymol_cmd, capsys):
    pymol_cmd.get_object_list.return_value = ["a"]
    color_group_with_palette("g", "earth", auto_register=False, verbose=True)
    out = capsys.readouterr().out
    assert "earth" in out
    assert "a" in out


# ---------------------------------------------------------------------------
# color_group_with_gradient
# ---------------------------------------------------------------------------


def test_color_group_with_gradient_happy_path(pymol_cmd):
    pymol_cmd.get_object_list.return_value = ["a", "b", "c"]
    pymol_cmd.get_color_tuple.return_value = (0.0, 0.0, 1.0)  # blue

    result = color_group_with_gradient("grp", "blue", verbose=False)
    assert set(result.keys()) == {"a", "b", "c"}
    assert pymol_cmd.set_color.call_count == 3
    assert pymol_cmd.color.call_count == 3


def test_color_group_with_gradient_color_names_follow_convention(pymol_cmd):
    pymol_cmd.get_object_list.return_value = ["x", "y"]
    pymol_cmd.get_color_tuple.return_value = (1.0, 0.0, 0.0)

    result = color_group_with_gradient(
        "grp", "red", gradient_type="saturation", verbose=False
    )
    assert result["x"] == "gradient_saturation_01"
    assert result["y"] == "gradient_saturation_02"


def test_color_group_with_gradient_unknown_gradient_type_returns_empty(
    pymol_cmd, capsys
):
    pymol_cmd.get_object_list.return_value = ["a"]
    result = color_group_with_gradient(
        "grp", "blue", gradient_type="rainbow", verbose=False
    )
    assert result == {}
    assert "unknown gradient_type" in capsys.readouterr().out.lower()


def test_color_group_with_gradient_unknown_color_returns_empty(pymol_cmd, capsys):
    pymol_cmd.get_object_list.return_value = ["a"]
    pymol_cmd.get_color_tuple.side_effect = Exception("no such color")
    result = color_group_with_gradient("grp", "no_such_color", verbose=False)
    assert result == {}
    assert "unknown color" in capsys.readouterr().out.lower()


def test_color_group_with_gradient_no_objects_returns_empty(pymol_cmd, capsys):
    pymol_cmd.get_object_list.return_value = []
    pymol_cmd.count_atoms.return_value = 0
    result = color_group_with_gradient("empty", "blue", verbose=False)
    assert result == {}
    assert "no objects" in capsys.readouterr().out.lower()


def test_color_group_with_gradient_hue_type(pymol_cmd):
    pymol_cmd.get_object_list.return_value = ["a", "b"]
    pymol_cmd.get_color_tuple.return_value = (0.0, 1.0, 0.0)  # green

    result = color_group_with_gradient(
        "grp", "green", gradient_type="hue", verbose=False
    )
    assert len(result) == 2


def test_color_group_with_gradient_num_colors_parameter(pymol_cmd):
    """num_colors controls gradient resolution; all objects still get colored."""
    pymol_cmd.get_object_list.return_value = ["a", "b", "c"]
    pymol_cmd.get_color_tuple.return_value = (0.5, 0.5, 0.5)
    result = color_group_with_gradient("grp", "gray", num_colors=10, verbose=False)
    assert len(result) == 3
