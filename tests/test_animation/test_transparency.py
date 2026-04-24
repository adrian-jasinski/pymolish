"""Tests for ``pymolish.extensions.animation.transparency``."""

from __future__ import annotations

from pymolish.extensions.animation.transparency import (
    fade_in,
    fade_out,
    movie_transparency,
    set_frame_transparency,
    suggest_transparency_type,
    transparency_pulse,
    transparency_range,
    transparency_sequence,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_selection_valid(pymol_cmd, count: int = 10) -> None:
    """Configure mock so selection resolves to *count* atoms."""
    pymol_cmd.count_atoms.return_value = count


# ---------------------------------------------------------------------------
# suggest_transparency_type
# ---------------------------------------------------------------------------


def test_suggest_transparency_type_no_objects(pymol_cmd, capsys):
    pymol_cmd.get_object_list.return_value = []
    t, msg = suggest_transparency_type("all")
    assert t == 0
    assert "No objects" in msg


def test_suggest_transparency_type_returns_int(pymol_cmd):
    pymol_cmd.get_object_list.return_value = ["obj1"]
    pymol_cmd.get_setting_boolean.return_value = False
    t, msg = suggest_transparency_type("all")
    assert isinstance(t, int)
    assert isinstance(msg, str)


def test_suggest_transparency_type_cartoon(pymol_cmd):
    pymol_cmd.get_object_list.return_value = ["obj1"]

    def _get_bool(setting, obj):
        return setting == "cartoon"

    pymol_cmd.get_setting_boolean.side_effect = _get_bool
    t, msg = suggest_transparency_type("protein")
    assert t == 1
    assert "cartoon" in msg.lower()


def test_suggest_transparency_type_spheres(pymol_cmd):
    pymol_cmd.get_object_list.return_value = ["obj1"]

    def _get_bool(setting, obj):
        return setting == "spheres"

    pymol_cmd.get_setting_boolean.side_effect = _get_bool
    t, msg = suggest_transparency_type("protein")
    assert t == 2
    assert "sphere" in msg.lower()


# ---------------------------------------------------------------------------
# movie_transparency
# ---------------------------------------------------------------------------


def test_movie_transparency_applies_mdo_calls(pymol_cmd):
    _make_selection_valid(pymol_cmd)
    result = movie_transparency("protein", 1, 5, 0.0, 1.0, 0, "increase")
    assert result == 5
    assert pymol_cmd.mdo.call_count == 5


def test_movie_transparency_direction_decrease(pymol_cmd):
    _make_selection_valid(pymol_cmd)
    result = movie_transparency("protein", 1, 3, 0.0, 1.0, 0, "decrease")
    assert result == 3
    # First mdo call should set transparency=1.0 (actual_start when decreasing)
    first_call_args = pymol_cmd.mdo.call_args_list[0]
    cmd_str: str = first_call_args[0][1]
    assert "1.000" in cmd_str


def test_movie_transparency_bad_frame_order(pymol_cmd, capsys):
    result = movie_transparency("protein", 10, 5)
    assert result == 0
    assert "start_frame" in capsys.readouterr().out.lower()


def test_movie_transparency_invalid_transparency_value(pymol_cmd, capsys):
    result = movie_transparency("protein", 1, 5, start_transparency=1.5)
    assert result == 0
    assert "start_transparency" in capsys.readouterr().out.lower()


def test_movie_transparency_invalid_type(pymol_cmd, capsys):
    _make_selection_valid(pymol_cmd)
    result = movie_transparency("protein", 1, 5, transparency_type=9)
    assert result == 0
    assert "transparency_type" in capsys.readouterr().out.lower()


def test_movie_transparency_bad_direction(pymol_cmd, capsys):
    _make_selection_valid(pymol_cmd)
    result = movie_transparency("protein", 1, 5, direction="sideways")
    assert result == 0
    assert "direction" in capsys.readouterr().out.lower()


def test_movie_transparency_empty_selection(pymol_cmd, capsys):
    pymol_cmd.count_atoms.return_value = 0
    result = movie_transparency("chain Z", 1, 5)
    assert result == 0
    assert "no atoms" in capsys.readouterr().out.lower()


def test_movie_transparency_cgo_warns(pymol_cmd, capsys):
    _make_selection_valid(pymol_cmd)
    pymol_cmd.get_names.return_value = []
    result = movie_transparency("all", 1, 3, transparency_type=3)
    assert result == 3
    out = capsys.readouterr().out
    assert "cgo" in out.lower()


def test_movie_transparency_uses_cartoon_setting(pymol_cmd):
    _make_selection_valid(pymol_cmd)
    movie_transparency("protein", 1, 2, transparency_type=1)
    for call in pymol_cmd.mdo.call_args_list:
        assert "cartoon_transparency" in call[0][1]


def test_movie_transparency_single_frame(pymol_cmd):
    """start_frame == end_frame is rejected (must be strictly less)."""
    result = movie_transparency("all", 5, 5)
    assert result == 0


# ---------------------------------------------------------------------------
# fade_in / fade_out
# ---------------------------------------------------------------------------


def test_fade_in_delegates_to_movie_transparency(pymol_cmd):
    # fade_in passes start=1.0, end=0.0, direction="decrease" to movie_transparency.
    # direction="decrease" swaps: actual_start=end=0.0, actual_end=start=1.0.
    # Frames therefore run 0.0→1.0 (the PoC behaviour, faithfully preserved).
    _make_selection_valid(pymol_cmd)
    result = fade_in("protein", 1, 4)
    assert result == 4
    assert pymol_cmd.mdo.call_count == 4


def test_fade_out_delegates_to_movie_transparency(pymol_cmd):
    # fade_out passes start=0.0, end=1.0, direction="increase".
    # direction="increase": actual_start=0.0, actual_end=1.0.
    _make_selection_valid(pymol_cmd)
    result = fade_out("protein", 1, 4)
    assert result == 4
    assert pymol_cmd.mdo.call_count == 4


# ---------------------------------------------------------------------------
# transparency_pulse
# ---------------------------------------------------------------------------


def test_transparency_pulse_single_cycle(pymol_cmd):
    _make_selection_valid(pymol_cmd)
    result = transparency_pulse("all", 1, 10, 0.0, 1.0, 0, 1)
    assert result > 0
    assert pymol_cmd.mdo.call_count > 0


def test_transparency_pulse_bad_cycles(pymol_cmd, capsys):
    result = transparency_pulse("all", 1, 60, cycles=0)
    assert result == 0
    assert "cycles" in capsys.readouterr().out.lower()


def test_transparency_pulse_too_few_frames(pymol_cmd, capsys):
    result = transparency_pulse("all", 1, 2, cycles=5)
    assert result == 0
    assert "frames" in capsys.readouterr().out.lower()


# ---------------------------------------------------------------------------
# set_frame_transparency
# ---------------------------------------------------------------------------


def test_set_frame_transparency_success(pymol_cmd):
    _make_selection_valid(pymol_cmd)
    result = set_frame_transparency("protein", 50, 0.5, 1)
    assert result is True
    assert pymol_cmd.mdo.call_count == 1
    call_str: str = pymol_cmd.mdo.call_args[0][1]
    assert "cartoon_transparency" in call_str
    assert "0.500" in call_str


def test_set_frame_transparency_invalid_value(pymol_cmd, capsys):
    result = set_frame_transparency("protein", 1, 1.5, 0)
    assert result is False
    assert "transparency" in capsys.readouterr().out.lower()


def test_set_frame_transparency_invalid_type(pymol_cmd, capsys):
    _make_selection_valid(pymol_cmd)
    result = set_frame_transparency("protein", 1, 0.5, 9)
    assert result is False
    assert "transparency_type" in capsys.readouterr().out.lower()


def test_set_frame_transparency_empty_selection(pymol_cmd, capsys):
    pymol_cmd.count_atoms.return_value = 0
    result = set_frame_transparency("chain Z", 1, 0.5, 0)
    assert result is False
    assert "no atoms" in capsys.readouterr().out.lower()


def test_set_frame_transparency_cmd_exception(pymol_cmd, capsys):
    _make_selection_valid(pymol_cmd)
    pymol_cmd.mdo.side_effect = RuntimeError("mdo failed")
    result = set_frame_transparency("protein", 1, 0.5, 0)
    assert result is False
    assert "failed" in capsys.readouterr().out.lower()


# ---------------------------------------------------------------------------
# transparency_sequence
# ---------------------------------------------------------------------------


def test_transparency_sequence_parses_pairs(pymol_cmd):
    _make_selection_valid(pymol_cmd)
    result = transparency_sequence("protein", "100:0.0,110:0.5,120:1.0", 1)
    assert result == 3
    assert pymol_cmd.mdo.call_count == 3


def test_transparency_sequence_missing_pairs(pymol_cmd, capsys):
    result = transparency_sequence("protein", None)
    assert result == 0
    assert "required" in capsys.readouterr().out.lower()


def test_transparency_sequence_bad_format(pymol_cmd, capsys):
    result = transparency_sequence("protein", "bad-data", 1)
    assert result == 0
    assert "parse" in capsys.readouterr().out.lower()


# ---------------------------------------------------------------------------
# transparency_range
# ---------------------------------------------------------------------------


def test_transparency_range_applies_stepped_values(pymol_cmd):
    _make_selection_valid(pymol_cmd)
    result = transparency_range("protein", 1, 5, 0.0, 0.1, "increase", 0)
    assert result == 5
    assert pymol_cmd.mdo.call_count == 5
    # Frame 1 should be 0.000, frame 5 should be 0.400
    first: str = pymol_cmd.mdo.call_args_list[0][0][1]
    last: str = pymol_cmd.mdo.call_args_list[4][0][1]
    assert "0.000" in first
    assert "0.400" in last


def test_transparency_range_clamping(pymol_cmd):
    """Values beyond 1.0 must be clamped to 1.0."""
    _make_selection_valid(pymol_cmd)
    result = transparency_range("protein", 1, 5, 0.9, 0.5, "increase", 0)
    assert result == 5
    last: str = pymol_cmd.mdo.call_args_list[4][0][1]
    val = float(last.split(",")[1].strip())
    assert val <= 1.0


def test_transparency_range_bad_frame_order(pymol_cmd, capsys):
    result = transparency_range("protein", 10, 5)
    assert result == 0
    assert "start_frame" in capsys.readouterr().out.lower()


def test_transparency_range_bad_step(pymol_cmd, capsys):
    _make_selection_valid(pymol_cmd)
    result = transparency_range("protein", 1, 5, step=-0.1)
    assert result == 0
    assert "step" in capsys.readouterr().out.lower()


def test_transparency_range_bad_direction(pymol_cmd, capsys):
    _make_selection_valid(pymol_cmd)
    result = transparency_range("protein", 1, 5, direction="up")
    assert result == 0
    assert "direction" in capsys.readouterr().out.lower()
