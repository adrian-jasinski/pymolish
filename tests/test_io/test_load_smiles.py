"""Tests for ``pymolish.extensions.io.load_smiles`` (real RDKit, mocked cmd)."""

from __future__ import annotations

import builtins
from unittest.mock import call

import pytest

from pymolish.extensions.io import load_smiles as mod

pytest.importorskip("rdkit")


@pytest.fixture(autouse=True)
def _legal_names(pymol_cmd):
    pymol_cmd.get_legal_name.side_effect = lambda name: name


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


@pytest.mark.parametrize("suffix", [".smi", ".smiles", ".txt", ".SMI", ".TXT"])
@pytest.mark.parametrize("separator", [" ", "\t"])
def test_text_files_read_first_column_and_ignore_metadata(
    pymol_cmd, tmp_path, suffix, separator
):
    path = tmp_path / f"ligands{suffix}"
    path.write_text(
        "\ufeff# molecules\n\n"
        + separator.join(["SMILES", "name", "ID", "score"])
        + "\n"
        + separator.join(["CCO", "ethanol", "L001", "1.2"])
        + "\n"
        + separator.join(["CCN", "ethylamine", "L002", "2.4"])
        + "\n",
        encoding="utf-8",
    )
    assert mod.load_smiles(path, n_conformers=1) == ["ethanol", "ethylamine"]


@pytest.mark.parametrize("separator", [",", ";"])
@pytest.mark.parametrize("header", [True, False])
def test_csv_files_detect_separator_and_name_column(
    pymol_cmd, tmp_path, separator, header
):
    path = tmp_path / "ligands.CSV"
    lines = ['CCO{0}"ethanol, alcohol; sample"{0}L001', 'CCN{0}"amine"{0}L002{0}extra']
    if header:
        lines.insert(0, "SMILES{0}name{0}ID")
    path.write_text(
        "\ufeff# molecules\n\n" + "\n".join(line.format(separator) for line in lines),
        encoding="utf-8",
    )
    assert mod.load_smiles(path, n_conformers=1, name_column="3") == ["L001", "L002"]


@pytest.mark.parametrize("suffix", [".smi", ".csv"])
def test_single_file_entry_uses_label_before_name(pymol_cmd, tmp_path, suffix):
    path = tmp_path / f"single{suffix}"
    path.write_text("CCO,ethanol\n" if suffix == ".csv" else "CCO ethanol\n")
    assert mod.load_smiles(path, "fallback", 1) == ["ethanol"]


def test_csv_quoted_labels_are_normalized_by_pymol(pymol_cmd, tmp_path):
    path = tmp_path / "names.csv"
    path.write_text('SMILES,name\nCCO,"ethyl, alcohol"\nCCN,"ethyl\namine"\n')
    labels = {"ethyl, alcohol": "ethyl__alcohol", "ethyl\namine": "ethyl_amine"}
    pymol_cmd.get_legal_name.side_effect = labels.__getitem__
    assert mod.load_smiles(path, n_conformers=1) == ["ethyl__alcohol", "ethyl_amine"]
    assert pymol_cmd.get_legal_name.call_args_list == [call(label) for label in labels]


def test_name_column_zero_ignores_labels(pymol_cmd, tmp_path):
    path = tmp_path / "names.smi"
    path.write_text("CCO ethanol\nCCN ethylamine\n")
    pymol_cmd.get_unused_name.side_effect = ["lig01", "lig02"]
    assert mod.load_smiles(path, "lig", 1, name_column="0") == ["lig01", "lig02"]


@pytest.mark.parametrize("contents", ["CCO\nCCN\n", "CCO,,metadata\nCCN\n"])
def test_missing_csv_names_use_prefix(pymol_cmd, tmp_path, contents):
    path = tmp_path / "names.csv"
    path.write_text(contents)
    pymol_cmd.get_unused_name.side_effect = ["lig01", "lig02"]
    assert mod.load_smiles(path, "lig", 1) == ["lig01", "lig02"]


def test_tab_file_preserves_empty_name_column(pymol_cmd, tmp_path):
    path = tmp_path / "names.txt"
    path.write_text("CCO\t\tmetadata\nCCN\tamine\tother\n")
    pymol_cmd.get_unused_name.return_value = "mol01"
    assert mod.load_smiles(path, n_conformers=1) == ["mol01", "amine"]


def test_quoted_home_path_is_detected(pymol_cmd, tmp_path, monkeypatch):
    path = tmp_path / "my ligands.smi"
    path.write_text("CCO ethanol\n")
    monkeypatch.setattr(
        mod.os.path,
        "expanduser",
        lambda arg: str(path) if arg == "~/my ligands.smi" else arg,
    )
    assert mod.load_smiles('"~/my ligands.smi"', n_conformers=1) == ["ethanol"]


def test_existing_file_without_suffix_is_detected(pymol_cmd, tmp_path):
    path = tmp_path / "ligands"
    path.write_text("CCO ethanol\n")
    assert mod.load_smiles(path, n_conformers=1) == ["ethanol"]


def test_inline_stereochemical_smiles_is_not_a_path(pymol_cmd):
    assert mod.load_smiles("F/C=C/F", "difluoroethene", 1, name_column=3) == [
        "difluoroethene"
    ]


def test_duplicate_and_existing_names_do_not_overwrite(pymol_cmd, tmp_path):
    path = tmp_path / "duplicates.smi"
    path.write_text("CCO ligand\nCCN ligand\n")
    pymol_cmd.get_names.return_value = ["ligand", "ligand_2"]
    assert mod.load_smiles(path, n_conformers=1) == ["ligand_3", "ligand_4"]
    assert _molstr_calls(pymol_cmd) == [("ligand_3", 1), ("ligand_4", 1)]


def test_conformer_names_do_not_overwrite_existing_objects(pymol_cmd):
    pymol_cmd.get_names.return_value = ["butanol_1"]
    assert mod.load_smiles("CCCCO", "butanol", 3) == [
        "butanol_2_1",
        "butanol_2_2",
        "butanol_2_3",
    ]


@pytest.mark.parametrize("mode", ["objects", "states"])
def test_parent_group_preserves_conformer_groups(pymol_cmd, tmp_path, mode):
    path = tmp_path / "ligands.smi"
    path.write_text("CCCCO butanol\nCCO ethanol\n")
    result = mod.load_smiles(path, n_conformers=3, mode=mode, group_name='"screen"')
    expected = (
        ["butanol", "ethanol"]
        if mode == "states"
        else ["butanol_1", "butanol_2", "butanol_3", "ethanol"]
    )
    assert result == expected
    group_calls = (
        [] if mode == "states" else [call("butanol", "butanol_1 butanol_2 butanol_3")]
    )
    assert pymol_cmd.group.call_args_list == group_calls + [
        call("screen", "butanol", action="add"),
        call("screen", "ethanol", action="add"),
    ]


def test_inline_molecule_can_join_existing_group(pymol_cmd):
    pymol_cmd.get_names.return_value = ["screen"]
    pymol_cmd.get_type.return_value = "object:group"
    assert mod.load_smiles("CCO", "ethanol", 1, group_name="screen") == ["ethanol"]
    pymol_cmd.group.assert_called_once_with("screen", "ethanol", action="add")


def test_parent_group_name_is_reserved(pymol_cmd):
    assert mod.load_smiles("CCO", "screen", 1, group_name="screen") == ["screen_2"]
    pymol_cmd.group.assert_called_once_with("screen", "screen_2", action="add")


def test_parent_group_collision_prevents_loading(pymol_cmd, capsys):
    pymol_cmd.get_names.return_value = ["screen"]
    pymol_cmd.get_type.return_value = "object:molecule"
    assert mod.load_smiles("CCO", "ethanol", 1, group_name="screen") == []
    assert "parent group" in capsys.readouterr().out
    pymol_cmd.read_molstr.assert_not_called()
    pymol_cmd.group.assert_not_called()


def test_invalid_file_molecule_is_skipped(pymol_cmd, tmp_path, capsys):
    path = tmp_path / "mixed.smi"
    path.write_text("C1CC bad\nCCO ethanol\n")
    assert mod.load_smiles(path, n_conformers=1, group_name="screen") == ["ethanol"]
    assert "invalid SMILES" in capsys.readouterr().out
    pymol_cmd.group.assert_called_once_with("screen", "ethanol", action="add")


@pytest.mark.parametrize(
    "contents", ["", "# comment\n\n", "SMILES name\n", "C1CC bad\n"]
)
def test_no_loaded_molecules_does_not_create_group(pymol_cmd, tmp_path, contents):
    path = tmp_path / "empty.smi"
    path.write_text(contents)
    assert mod.load_smiles(path, group_name="screen") == []
    pymol_cmd.read_molstr.assert_not_called()
    pymol_cmd.group.assert_not_called()


def test_missing_file_reports_read_error(pymol_cmd, tmp_path, capsys):
    assert mod.load_smiles(tmp_path / "missing.smi") == []
    assert "could not read" in capsys.readouterr().out
    pymol_cmd.read_molstr.assert_not_called()


@pytest.mark.parametrize(
    "error", [PermissionError("permission denied"), UnicodeError("invalid UTF-8")]
)
def test_unreadable_file_reports_error(pymol_cmd, tmp_path, monkeypatch, capsys, error):
    path = tmp_path / "unreadable.smi"

    def fail_open(*args, **kwargs):
        raise error

    monkeypatch.setattr(mod, "open", fail_open, raising=False)
    assert mod.load_smiles(path) == []
    assert "could not read" in capsys.readouterr().out
    pymol_cmd.read_molstr.assert_not_called()


def test_malformed_csv_does_not_partially_load(pymol_cmd, tmp_path, capsys):
    path = tmp_path / "malformed.csv"
    path.write_text('CCO,ethanol\nCCN,"unfinished\n')
    assert mod.load_smiles(path) == []
    assert "malformed CSV" in capsys.readouterr().out
    pymol_cmd.read_molstr.assert_not_called()


@pytest.mark.parametrize(
    "kwargs",
    [
        {"name_column": -1},
        {"name_column": "bad"},
        {"n_conformers": "bad"},
        {"seed": "bad"},
    ],
)
def test_invalid_numeric_arguments_report_errors(pymol_cmd, capsys, kwargs):
    assert mod.load_smiles("CCO", **kwargs) == []
    assert "invalid numeric argument" in capsys.readouterr().out
    pymol_cmd.read_molstr.assert_not_called()


def test_group_failure_keeps_loaded_objects(pymol_cmd, capsys):
    pymol_cmd.group.side_effect = RuntimeError("grouping failed")
    assert mod.load_smiles("CCO", "ethanol", 1, group_name="screen") == ["ethanol"]
    assert "failed to group" in capsys.readouterr().out


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
