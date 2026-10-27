"""Tests for ``pymolish.extensions.selection.solvent``."""

from __future__ import annotations

from pymolish.extensions.selection.solvent import ION_SELECTION, ions, water


def test_water_selects_and_increments(pymol_cmd):
    pymol_cmd.get_names.return_value = ["water", "water1"]
    assert water() == "water2"
    pymol_cmd.select.assert_called_once_with("water2", "solvent")


def test_water_on_off(pymol_cmd):
    assert water("on") == ""
    pymol_cmd.show.assert_called_once_with("lines", "solvent")
    assert water("off") == ""
    pymol_cmd.hide.assert_called_once_with("everything", "solvent")


def test_ions_selects(pymol_cmd):
    assert ions() == "ions"
    pymol_cmd.select.assert_called_once_with("ions", ION_SELECTION)
    assert "resn NA+K+CL+MG" in ION_SELECTION
