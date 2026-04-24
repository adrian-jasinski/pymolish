"""Tests for ``pymolish.extensions.visualization.palettes``."""

from __future__ import annotations

from pymolish.extensions.visualization.palettes import (
    CARTOON_PALETTES,
    COLOR_PALETTES,
    PALETTE_DESCRIPTIONS,
    list_available_palettes,
    register_extended_colors,
)

# ---------------------------------------------------------------------------
# Data integrity
# ---------------------------------------------------------------------------


def test_color_palettes_have_expected_keys():
    expected = {"pastels", "neon", "earth", "ocean", "warm", "cool"}
    assert set(COLOR_PALETTES.keys()) == expected


def test_each_color_palette_has_25_entries():
    for name, colors in COLOR_PALETTES.items():
        assert len(colors) == 25, f"palette '{name}' should have 25 colors"


def test_each_color_is_valid_rgb_tuple():
    for name, colors in COLOR_PALETTES.items():
        for i, entry in enumerate(colors):
            r, g, b = entry
            assert 0.0 <= r <= 1.0, f"{name}[{i}] red out of range"
            assert 0.0 <= g <= 1.0, f"{name}[{i}] green out of range"
            assert 0.0 <= b <= 1.0, f"{name}[{i}] blue out of range"


def test_all_palettes_have_descriptions():
    for name in COLOR_PALETTES:
        assert name in PALETTE_DESCRIPTIONS


def test_cartoon_palettes_required_keys():
    required = {"helix", "sheet", "loop", "description"}
    for name, info in CARTOON_PALETTES.items():
        assert required <= set(info.keys()), f"'{name}' missing keys"


def test_cartoon_palettes_has_expected_count():
    assert len(CARTOON_PALETTES) == 10


# ---------------------------------------------------------------------------
# register_extended_colors
# ---------------------------------------------------------------------------


def test_register_extended_colors_registers_all_palettes(pymol_cmd):
    count = register_extended_colors(verbose=False)
    total = sum(len(v) for v in COLOR_PALETTES.values())
    assert count == total
    assert pymol_cmd.set_color.call_count == total


def test_register_extended_colors_single_palette(pymol_cmd):
    count = register_extended_colors("pastels", verbose=False)
    assert count == 25
    assert pymol_cmd.set_color.call_count == 25


def test_register_extended_colors_unknown_palette_returns_zero(pymol_cmd, capsys):
    count = register_extended_colors("no_such_palette", verbose=False)
    assert count == 0
    pymol_cmd.set_color.assert_not_called()
    out = capsys.readouterr().out
    assert "unknown palette" in out.lower()


def test_register_extended_colors_verbose_logs_each_color(pymol_cmd, capsys):
    register_extended_colors("neon", verbose=True)
    out = capsys.readouterr().out
    assert "neon_01" in out
    assert "registered" in out.lower()


def test_register_extended_colors_color_names_follow_convention(pymol_cmd):
    register_extended_colors("pastels", verbose=False)
    calls = pymol_cmd.set_color.call_args_list
    names = [c.args[0] for c in calls]
    assert names[0] == "pastels_01"
    assert names[-1] == "pastels_25"


# ---------------------------------------------------------------------------
# list_available_palettes
# ---------------------------------------------------------------------------


def test_list_available_palettes_returns_all_names(pymol_cmd, capsys):
    names = list_available_palettes()
    assert set(names) == set(COLOR_PALETTES.keys())


def test_list_available_palettes_prints_descriptions(pymol_cmd, capsys):
    list_available_palettes()
    out = capsys.readouterr().out
    assert "pastels" in out
    assert "neon" in out
    assert "preview" in out.lower()
