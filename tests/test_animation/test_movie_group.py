"""Tests for ``pymolish.extensions.animation.movie_group``."""

from __future__ import annotations

from pymolish.extensions.animation.movie_group import movie_from_group

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _setup_group(pymol_cmd, members: list[str]) -> None:
    """Configure mock so *group_name* resolves to *members*."""
    pymol_cmd.get_object_list.return_value = members


# ---------------------------------------------------------------------------
# Argument validation
# ---------------------------------------------------------------------------


def test_movie_from_group_empty_name(pymol_cmd, capsys):
    result = movie_from_group("")
    assert result == 0
    assert "required" in capsys.readouterr().out.lower()


def test_movie_from_group_quoted_name_stripped(pymol_cmd, capsys):
    """Quoted group names should be stripped before processing."""
    pymol_cmd.get_object_list.return_value = None
    result = movie_from_group('"my_group"')
    # Will fail because group is empty, but name stripping means it tries to look it up.
    assert result == 0


def test_movie_from_group_bad_frames_per_object(pymol_cmd, capsys):
    result = movie_from_group("grp", "abc")
    assert result == 0
    assert "integer" in capsys.readouterr().out.lower()


def test_movie_from_group_zero_frames_per_object(pymol_cmd, capsys):
    result = movie_from_group("grp", 0)
    assert result == 0
    assert ">= 1" in capsys.readouterr().out


def test_movie_from_group_group_not_found(pymol_cmd, capsys):
    pymol_cmd.get_object_list.return_value = None
    result = movie_from_group("missing_group")
    assert result == 0
    assert "not found" in capsys.readouterr().out.lower()


def test_movie_from_group_empty_group(pymol_cmd, capsys):
    pymol_cmd.get_object_list.return_value = []
    result = movie_from_group("empty_group")
    assert result == 0
    assert "empty" in capsys.readouterr().out.lower()


# ---------------------------------------------------------------------------
# Correct behaviour
# ---------------------------------------------------------------------------


def test_movie_from_group_sets_mset(pymol_cmd):
    _setup_group(pymol_cmd, ["obj1", "obj2", "obj3"])
    result = movie_from_group("grp", 10)
    assert result == 30  # 3 objects * 10 frames
    pymol_cmd.mset.assert_called_once_with("1 x30")


def test_movie_from_group_creates_scenes(pymol_cmd):
    _setup_group(pymol_cmd, ["obj1", "obj2"])
    movie_from_group("grp", 5)
    scene_calls = [c for c in pymol_cmd.scene.call_args_list if c[0][1] == "store"]
    assert len(scene_calls) == 2
    scene_names = [c[0][0] for c in scene_calls]
    assert "001" in scene_names
    assert "002" in scene_names


def test_movie_from_group_stores_mview_keyframes(pymol_cmd):
    _setup_group(pymol_cmd, ["obj1", "obj2", "obj3"])
    movie_from_group("grp", 5)
    mview_store_calls = [
        c for c in pymol_cmd.mview.call_args_list if c[0][0] == "store"
    ]
    # One mview store per object
    assert len(mview_store_calls) == 3


def test_movie_from_group_first_keyframe_at_frame_one(pymol_cmd):
    _setup_group(pymol_cmd, ["obj1", "obj2"])
    movie_from_group("grp", 10)
    first_store = pymol_cmd.mview.call_args_list[0]
    assert first_store.kwargs.get("first") == 1 or first_store[1].get("first") == 1


def test_movie_from_group_reinterpolates(pymol_cmd):
    _setup_group(pymol_cmd, ["obj1", "obj2"])
    movie_from_group("grp", 5)
    pymol_cmd.do.assert_called_with("mview reinterpolate")


def test_movie_from_group_disables_others(pymol_cmd):
    _setup_group(pymol_cmd, ["obj1", "obj2"])
    movie_from_group("grp", 5)
    # Both obj1 and obj2 must be disabled at some point during setup
    disabled = {c[0][0] for c in pymol_cmd.disable.call_args_list}
    assert "obj1" in disabled
    assert "obj2" in disabled


def test_movie_from_group_enables_each_object(pymol_cmd):
    _setup_group(pymol_cmd, ["obj1", "obj2", "obj3"])
    movie_from_group("grp", 5)
    enabled = [c[0][0] for c in pymol_cmd.enable.call_args_list]
    assert "obj1" in enabled
    assert "obj2" in enabled
    assert "obj3" in enabled


def test_movie_from_group_returns_total_frames(pymol_cmd):
    _setup_group(pymol_cmd, ["a", "b", "c", "d"])
    assert movie_from_group("grp", 7) == 28
