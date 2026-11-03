"""Tests for ``pymolish.extensions.visualization.plddt``."""

from __future__ import annotations

from pymolish.extensions.visualization.plddt import color_plddt


def test_gradient_spectrum_and_legend(pymol_cmd):
    pymol_cmd.count_atoms.return_value = 42
    pymol_cmd.get_object_list.return_value = ["m"]

    assert color_plddt("m", palette="gradient") == 42
    pymol_cmd.spectrum.assert_called_once_with(
        "b", "red_yellow_blue", "m", minimum=0, maximum=100
    )
    pymol_cmd.delete.assert_called_once_with("AF_pLDDT_legend")
    name, obj, values, _colors = pymol_cmd.ramp_new.call_args[0]
    assert (name, obj, values[0], values[-1]) == ("AF_pLDDT_legend", "m", 0, 100)


def test_af_bins_default_and_no_legend(pymol_cmd):
    pymol_cmd.count_atoms.return_value = 5
    assert color_plddt("m", legend=0) == 5
    assert pymol_cmd.color.call_count == 4
    pymol_cmd.spectrum.assert_not_called()
    pymol_cmd.ramp_new.assert_not_called()


def test_empty_selection_and_bad_palette(pymol_cmd):
    assert color_plddt("nothing") == 0
    pymol_cmd.count_atoms.return_value = 1
    assert color_plddt("m", palette="rainbow") == 0
    pymol_cmd.spectrum.assert_not_called()
