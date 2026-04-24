"""Tests for ``pymolish.extensions.visualization.color_ss``."""

from __future__ import annotations

from pymolish.extensions.visualization.color_ss import (
    color_secondary_structure,
    list_cartoon_palettes,
)
from pymolish.extensions.visualization.palettes import CARTOON_PALETTES

# ---------------------------------------------------------------------------
# color_secondary_structure
# ---------------------------------------------------------------------------


def test_color_secondary_structure_colors_all_elements(pymol_cmd):
    pymol_cmd.get_object_list.return_value = ["my_protein"]
    pymol_cmd.count_atoms.return_value = 10  # every element has atoms

    result = color_secondary_structure("my_protein", "ard", verbose=False)

    assert result["palette"] == "ard"
    assert "helices" in result
    assert "sheets" in result
    assert "loops" in result
    assert pymol_cmd.color.call_count == 3


def test_color_secondary_structure_applies_correct_colors(pymol_cmd):
    pymol_cmd.get_object_list.return_value = ["prot"]
    pymol_cmd.count_atoms.return_value = 5

    result = color_secondary_structure("prot", "sunset", verbose=False)

    assert result["helices"]["color"] == "red"
    assert result["sheets"]["color"] == "cyan"
    assert result["loops"]["color"] == "salmon"


def test_color_secondary_structure_unknown_palette_returns_empty(pymol_cmd, capsys):
    result = color_secondary_structure("prot", "fantasy", verbose=False)
    assert result == {}
    assert "unknown palette" in capsys.readouterr().out.lower()


def test_color_secondary_structure_object_not_found_returns_empty(pymol_cmd, capsys):
    pymol_cmd.get_object_list.return_value = ["other_obj"]
    result = color_secondary_structure("missing_obj", "ard", verbose=False)
    assert result == {}
    assert "not found" in capsys.readouterr().out.lower()


def test_color_secondary_structure_skips_empty_elements(pymol_cmd):
    pymol_cmd.get_object_list.return_value = ["prot"]

    # Only sheets have atoms; helices and loops are empty
    def atom_count_side_effect(selection):
        if "ss s" in selection:
            return 20
        return 0

    pymol_cmd.count_atoms.side_effect = atom_count_side_effect

    result = color_secondary_structure("prot", "royal", verbose=False)
    assert "sheets" in result
    assert "helices" not in result
    assert "loops" not in result
    assert pymol_cmd.color.call_count == 1


def test_color_secondary_structure_verbose_logs(pymol_cmd, capsys):
    pymol_cmd.get_object_list.return_value = ["prot"]
    pymol_cmd.count_atoms.return_value = 8

    color_secondary_structure("prot", "forest", verbose=True)
    out = capsys.readouterr().out
    assert "forest" in out
    assert "prot" in out


def test_color_secondary_structure_returns_description(pymol_cmd):
    pymol_cmd.get_object_list.return_value = ["p"]
    pymol_cmd.count_atoms.return_value = 3

    result = color_secondary_structure("p", "monochrome", verbose=False)
    expected_desc = CARTOON_PALETTES["monochrome"]["description"]
    assert result["description"] == expected_desc


# ---------------------------------------------------------------------------
# list_cartoon_palettes
# ---------------------------------------------------------------------------


def test_list_cartoon_palettes_returns_all_names(pymol_cmd, capsys):
    names = list_cartoon_palettes()
    assert set(names) == set(CARTOON_PALETTES.keys())


def test_list_cartoon_palettes_prints_palette_details(pymol_cmd, capsys):
    list_cartoon_palettes()
    out = capsys.readouterr().out
    assert "ard" in out
    assert "helix" in out.lower()
    assert "sheet" in out.lower()
    assert "loop" in out.lower()
