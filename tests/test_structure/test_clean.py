"""Tests for ``pymolish.extensions.structure.clean``."""

from __future__ import annotations

from pymolish.extensions.structure.clean import (
    _IONS,
    _METALS,
    remove_ions,
    remove_metals,
)

# ---------------------------------------------------------------------------
# remove_ions
# ---------------------------------------------------------------------------


def test_remove_ions_calls_remove_for_matching_residues(pymol_cmd):
    # Only "NA" has atoms; everything else returns 0
    def count_side(sel):
        return 5 if "NA" in sel else 0

    pymol_cmd.count_atoms.side_effect = count_side
    result = remove_ions("all")
    assert result == 1  # one ion type removed
    pymol_cmd.remove.assert_called_once()
    assert "NA" in pymol_cmd.remove.call_args.args[0]


def test_remove_ions_no_atoms_skips_remove(pymol_cmd):
    pymol_cmd.count_atoms.return_value = 0
    result = remove_ions("all")
    assert result == 0
    pymol_cmd.remove.assert_not_called()


def test_remove_ions_multiple_matches(pymol_cmd):
    def count_side(sel):
        # NA and K have atoms
        if "resn NA" in sel or "resn K" in sel:
            return 3
        return 0

    pymol_cmd.count_atoms.side_effect = count_side
    result = remove_ions("all")
    assert result == 2


def test_remove_ions_uses_default_selection(pymol_cmd):
    pymol_cmd.count_atoms.return_value = 0
    remove_ions()
    # Verify the selection "all" was used somewhere in a count_atoms call
    calls_args = [str(c) for c in pymol_cmd.count_atoms.call_args_list]
    assert any("all" in a for a in calls_args)


def test_remove_ions_custom_selection(pymol_cmd):
    pymol_cmd.count_atoms.return_value = 0
    remove_ions("chain A")
    calls_args = [str(c) for c in pymol_cmd.count_atoms.call_args_list]
    assert any("chain A" in a for a in calls_args)


def test_remove_ions_handles_remove_error(pymol_cmd, capsys):
    pymol_cmd.count_atoms.return_value = 1
    pymol_cmd.remove.side_effect = Exception("pymol error")
    # Should not raise; errors are logged as warnings
    remove_ions("all")
    out = capsys.readouterr().out
    assert "warn" in out.lower() or "failed" in out.lower()


def test_remove_ions_logs_summary(pymol_cmd, capsys):
    pymol_cmd.count_atoms.return_value = 0
    remove_ions()
    out = capsys.readouterr().out
    assert "removing ions" in out.lower()
    assert "removed" in out.lower()


# ---------------------------------------------------------------------------
# remove_metals
# ---------------------------------------------------------------------------


def test_remove_metals_calls_remove_for_matching_residues(pymol_cmd):
    def count_side(sel):
        return 5 if "ZN" in sel else 0

    pymol_cmd.count_atoms.side_effect = count_side
    result = remove_metals("all")
    assert result == 1
    pymol_cmd.remove.assert_called_once()
    assert "ZN" in pymol_cmd.remove.call_args.args[0]


def test_remove_metals_no_atoms_skips_remove(pymol_cmd):
    pymol_cmd.count_atoms.return_value = 0
    result = remove_metals("all")
    assert result == 0
    pymol_cmd.remove.assert_not_called()


def test_remove_metals_uses_default_selection(pymol_cmd):
    pymol_cmd.count_atoms.return_value = 0
    remove_metals()
    calls_args = [str(c) for c in pymol_cmd.count_atoms.call_args_list]
    assert any("all" in a for a in calls_args)


def test_remove_metals_logs_summary(pymol_cmd, capsys):
    pymol_cmd.count_atoms.return_value = 0
    remove_metals()
    out = capsys.readouterr().out
    assert "removing metals" in out.lower()
    assert "removed" in out.lower()


def test_remove_metals_curated_list_is_nonempty():
    assert len(_METALS) > 10


def test_remove_ions_curated_list_is_nonempty():
    assert len(_IONS) > 5
