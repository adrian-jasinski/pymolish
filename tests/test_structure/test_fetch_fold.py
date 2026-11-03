"""Tests for ``pymolish.extensions.structure.fetch_fold``."""

from __future__ import annotations

import json
import urllib.error

from pymolish.extensions.structure import fetch_fold as mod
from pymolish.extensions.structure.fetch_fold import fetch_fold

_SEQ = "MKTAYIAKQRQISFVKSHFSRQ"
_PDB = "ATOM      1  N   MET A   1       0.000   0.000   0.000  1.00 95.00\nEND\n"


def _http(monkeypatch, routes):
    """Patch ``_http_text`` with a dict of URL-prefix -> response (str or exc)."""
    calls = []

    def fake(url, data=None, timeout=120):
        calls.append((url, data))
        for prefix, resp in routes.items():
            if url.startswith(prefix):
                if isinstance(resp, Exception):
                    raise resp
                return resp
        raise AssertionError(f"unexpected URL {url}")

    monkeypatch.setattr(mod, "_http_text", fake)
    return calls


def _not_found():
    return urllib.error.HTTPError("u", 404, "nf", {}, None)


def test_detection():
    assert mod._parse_af_model_id("AF-P04637-F1") == ("P04637", 1)
    assert mod._parse_af_model_id("af-q8wz42-f12-model_v4") == ("Q8WZ42", 12)
    assert mod._parse_af_model_id("P04637") is None
    assert mod._is_accession("P04637")
    assert mod._is_accession("A0A024R161")
    assert not mod._is_accession(_SEQ)
    assert mod._is_sequence("mkta yiak\n")
    assert not mod._is_sequence("P04637")  # contains digits


def test_accession_loads_from_alphafold(pymol_cmd, monkeypatch):
    calls = _http(
        monkeypatch,
        {
            "https://alphafold.ebi.ac.uk/api": json.dumps(
                [{"pdbUrl": "https://af/x.pdb"}]
            ),
            "https://af/": _PDB,
        },
    )
    pymol_cmd.count_atoms.return_value = 1
    pymol_cmd.get_object_list.return_value = ["AF_P04637"]

    assert fetch_fold("P04637") == "AF_P04637"
    pymol_cmd.read_pdbstr.assert_called_once_with(_PDB, "AF_P04637")
    assert pymol_cmd.color.call_count == 4
    pymol_cmd.ramp_new.assert_called_once()
    assert calls[0][0].endswith("/P04637")


def test_af_model_id_selects_fragment(pymol_cmd, monkeypatch):
    entries = [
        {"entryId": "AF-Q8WZ42-F1", "pdbUrl": "https://af/f1.pdb"},
        {"entryId": "AF-Q8WZ42-F2", "pdbUrl": "https://af/f2.pdb"},
    ]
    calls = _http(
        monkeypatch,
        {"https://alphafold.ebi.ac.uk/api": json.dumps(entries), "https://af/": _PDB},
    )
    assert fetch_fold("AF-Q8WZ42-F2-model_v4", color=0) == "AF_Q8WZ42_F2"
    assert calls[-1][0] == "https://af/f2.pdb"


def test_sequence_goes_to_esmfold(pymol_cmd, monkeypatch):
    calls = _http(monkeypatch, {"https://api.esmatlas.com": _PDB})
    pymol_cmd.count_atoms.return_value = 1
    pymol_cmd.get_object_list.return_value = ["x"]

    name = fetch_fold(_SEQ, color=0)
    assert name.startswith("ESM_")
    assert calls[0][1] == _SEQ.encode()
    pymol_cmd.color.assert_not_called()


def test_missing_accession_falls_back_to_esmfold(pymol_cmd, monkeypatch):
    calls = _http(
        monkeypatch,
        {
            "https://alphafold.ebi.ac.uk/api": _not_found(),
            "https://rest.uniprot.org": f">sp|X\n{_SEQ[:10]}\n{_SEQ[10:]}\n",
            "https://api.esmatlas.com": _PDB,
        },
    )
    assert fetch_fold("P04637", color=0) == "ESM_P04637"
    assert calls[-1][1] == _SEQ.encode()


def test_bad_query_and_network_error(pymol_cmd, monkeypatch, capsys):
    assert fetch_fold("not a protein!") is None
    _http(monkeypatch, {"https://alphafold.ebi.ac.uk": urllib.error.URLError("off")})
    assert fetch_fold("P04637") is None
    pymol_cmd.read_pdbstr.assert_not_called()
    assert "download failed" in capsys.readouterr().out
