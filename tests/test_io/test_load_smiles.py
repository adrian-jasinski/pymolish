"""Tests for ``pymolish.extensions.io.load_smiles`` (real RDKit, mocked cmd)."""

from __future__ import annotations

import builtins

import pytest

from pymolish.extensions.io import load_smiles as mod

pytest.importorskip("rdkit")


def _molstr_calls(pymol_cmd):
    calls = pymol_cmd.read_molstr.call_args_list
    return [(c.args[1], c.kwargs.get("state")) for c in calls]


def test_is_smiles_detects_molecules_and_rejects_text():
    assert mod.is_smiles("CC(=O)Oc1ccccc1C(=O)O")
    assert mod.is_smiles("  c1ccccc1 \n")
    assert not mod.is_smiles("hello world")
    assert not mod.is_smiles("not-a-molecule")
    assert not mod.is_smiles("")


def test_objects_mode_groups_conformers(pymol_cmd):
    pymol_cmd.get_unused_name.return_value = "mol01"
    result = mod.load_smiles("CCCCO", n_conformers="3")
    assert result == ["mol01_1", "mol01_2", "mol01_3"]
    assert [n for n, _ in _molstr_calls(pymol_cmd)] == result
    pymol_cmd.group.assert_called_once_with("mol01", "mol01_1 mol01_2 mol01_3")
    assert "V30" not in pymol_cmd.read_molstr.call_args.args[0]  # V2000 MOL block


def test_states_mode_single_object(pymol_cmd):
    assert mod.load_smiles("CCCCO", "butanol", 3, "states") == ["butanol"]
    assert _molstr_calls(pymol_cmd) == [("butanol", 1), ("butanol", 2), ("butanol", 3)]
    pymol_cmd.group.assert_not_called()


def test_single_conformer_is_plain_object(pymol_cmd):
    assert mod.load_smiles("C", "methane", 1) == ["methane"]
    pymol_cmd.group.assert_not_called()


def test_invalid_smiles_and_mode_report_errors(pymol_cmd, capsys):
    assert mod.load_smiles("C1CC", "bad") == []
    assert "invalid SMILES" in capsys.readouterr().out
    assert mod.load_smiles("C", "x", 1, "banana") == []
    assert "mode must be" in capsys.readouterr().out
    pymol_cmd.read_molstr.assert_not_called()


def test_smi_file_uses_line_names_then_prefix(pymol_cmd, tmp_path):
    smi = tmp_path / "ligs.smi"
    smi.write_text("# comment\nCCO ethanol\nCCN\n\n")
    pymol_cmd.get_unused_name.return_value = "lig01"
    assert mod.load_smiles(str(smi), "lig", 1) == ["ethanol", "lig01"]
    pymol_cmd.get_unused_name.assert_called_once_with("lig")


def test_paste_smiles_loads_clipboard_molecule(pymol_cmd, monkeypatch, capsys):
    monkeypatch.setattr(mod, "_clipboard_text", lambda: "CCCCO\n")
    pymol_cmd.get_unused_name.return_value = "mol01"
    assert mod.paste_smiles(2) == ["mol01_1", "mol01_2"]

    monkeypatch.setattr(mod, "_clipboard_text", lambda: "select resi 10")
    assert mod.paste_smiles() == []
    assert "not a SMILES" in capsys.readouterr().out


def test_missing_rdkit_gives_install_hint(pymol_cmd, monkeypatch, capsys):
    real_import = builtins.__import__

    def no_rdkit(name, *args, **kwargs):
        if name.startswith("rdkit"):
            raise ImportError("nope")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", no_rdkit)
    assert mod.load_smiles("C") == []
    assert mod.paste_smiles() == []
    out = capsys.readouterr().out
    assert out.count("pymolish_install_deps rdkit") == 2
