"""Tests for ``pymolish.extensions.structure.fetch_uniprot``."""

from __future__ import annotations

import sys
import urllib.error

from pymolish.extensions.structure import fetch_uniprot
from pymolish.extensions.structure.fetch_uniprot import (
    fetch_by_uniprot,
    list_uniprot_structures,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_DETAILS = {
    "struct": {"title": "Test protein"},
    "rcsb_entry_info": {"resolution_combined": 2.1},
    "exptl": [{"method": "X-RAY"}],
}


def _mock_http(monkeypatch, pdb_ids: list[str]):
    """Patch ``_http_json``: GraphQL POST returns *pdb_ids*, GETs return details."""

    def fake(url, payload=None, timeout=30):
        if payload is not None:
            return {
                "data": {"polymer_entities": [{"entry": {"id": p}} for p in pdb_ids]}
            }
        return _DETAILS

    monkeypatch.setattr(fetch_uniprot, "_http_json", fake)


def _fail_http(monkeypatch):
    def fake(url, payload=None, timeout=30):
        raise urllib.error.URLError("offline")

    monkeypatch.setattr(fetch_uniprot, "_http_json", fake)


def _block_biopython(monkeypatch):
    for mod in ("Bio", "Bio.ExPASy", "Bio.SwissProt"):
        monkeypatch.setitem(sys.modules, mod, None)


# ---------------------------------------------------------------------------
# Biopython is optional
# ---------------------------------------------------------------------------


def test_missing_biopython_skips_fallback_with_info(pymol_cmd, monkeypatch, capsys):
    _fail_http(monkeypatch)
    _block_biopython(monkeypatch)
    assert fetch_by_uniprot("P04637", verbose=False) == []
    out = capsys.readouterr().out
    assert "skipping ExPASy fallback" in out
    assert "WARNING" not in out.split("no PDB")[0]


def test_missing_biopython_not_mentioned_when_found(pymol_cmd, monkeypatch, capsys):
    _mock_http(monkeypatch, ["1TUP"])
    _block_biopython(monkeypatch)
    assert fetch_by_uniprot("P04637", verbose=False) == ["1TUP"]
    assert "biopython" not in capsys.readouterr().out


# ---------------------------------------------------------------------------
# fetch_by_uniprot
# ---------------------------------------------------------------------------


def test_fetch_by_uniprot_empty_id_returns_empty(pymol_cmd, monkeypatch, capsys):
    result = fetch_by_uniprot("", verbose=False)
    assert result == []
    assert "non-empty" in capsys.readouterr().out


def test_fetch_by_uniprot_no_structures_found(pymol_cmd, monkeypatch, capsys):
    _fail_http(monkeypatch)
    _block_biopython(monkeypatch)

    result = fetch_by_uniprot("ZZZZZZ", verbose=False)
    assert result == []
    assert "no pdb structures" in capsys.readouterr().out.lower()


def test_fetch_by_uniprot_happy(pymol_cmd, monkeypatch):
    _mock_http(monkeypatch, ["1TUP", "2OCJ"])

    result = fetch_by_uniprot("P04637", max_structures=10, verbose=False)
    assert "1TUP" in result or "2OCJ" in result
    assert pymol_cmd.fetch.call_count == len(result)


def test_fetch_by_uniprot_max_structures_limits_results(pymol_cmd, monkeypatch):
    _mock_http(monkeypatch, ["A000", "B001", "C002", "D003", "E004"])

    result = fetch_by_uniprot("P04637", max_structures=2, verbose=False)
    assert len(result) <= 2


def test_fetch_by_uniprot_handles_fetch_error(pymol_cmd, monkeypatch, capsys):
    _mock_http(monkeypatch, ["1TUP"])
    pymol_cmd.fetch.side_effect = Exception("network error")

    result = fetch_by_uniprot("P04637", verbose=True)
    assert result == []
    assert "failed" in capsys.readouterr().out.lower()


def test_fetch_by_uniprot_upcases_id(pymol_cmd, monkeypatch):
    _mock_http(monkeypatch, ["1TUP"])
    result = fetch_by_uniprot("p04637", max_structures=10, verbose=False)
    # The fetch call's object name should use the uppercased ID
    if result:
        obj_name = pymol_cmd.fetch.call_args_list[0].args[1]
        assert obj_name.startswith("P04637")


# ---------------------------------------------------------------------------
# list_uniprot_structures
# ---------------------------------------------------------------------------


def test_list_uniprot_structures_empty_id(pymol_cmd, monkeypatch, capsys):
    result = list_uniprot_structures("", show_details=False)
    assert result == []
    assert "non-empty" in capsys.readouterr().out


def test_list_uniprot_structures_returns_ids(pymol_cmd, monkeypatch, capsys):
    _mock_http(monkeypatch, ["1TUP", "2OCJ"])

    result = list_uniprot_structures("P04637", show_details=False)
    assert "1TUP" in result or "2OCJ" in result
    out = capsys.readouterr().out
    assert "found" in out.lower()


def test_list_uniprot_structures_no_fetch_call(pymol_cmd, monkeypatch):
    _mock_http(monkeypatch, ["1TUP"])

    list_uniprot_structures("P04637", show_details=False)
    pymol_cmd.fetch.assert_not_called()


def test_list_uniprot_structures_shows_details(pymol_cmd, monkeypatch, capsys):
    _mock_http(monkeypatch, ["1TUP"])
    list_uniprot_structures("P04637", show_details=True)
    assert "Test protein [X-RAY, 2.1" in capsys.readouterr().out


# ---------------------------------------------------------------------------
# fetch_uniprot_ligands
# ---------------------------------------------------------------------------


def test_fetch_uniprot_ligands_filters_by_weight(pymol_cmd, monkeypatch):
    comps = [("ZN", "ZINC ION", 65.4), ("AZM", "ACETAZOLAMIDE", 222.2)]

    def fake(url, payload=None, timeout=30):
        if "entries(" not in payload["query"]:
            return {"data": {"polymer_entities": [{"entry": {"id": "1CA2"}}]}}
        ents = [
            {
                "nonpolymer_comp": {
                    "chem_comp": {"id": i, "name": n, "formula_weight": w}
                }
            }
            for i, n, w in comps
        ]
        return {"data": {"entries": [{"nonpolymer_entities": ents}]}}

    class Resp:
        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def read(self):
            return b"sdf"

    monkeypatch.setattr(fetch_uniprot, "_http_json", fake)
    monkeypatch.setattr(fetch_uniprot.urllib.request, "urlopen", lambda *a, **k: Resp())
    monkeypatch.setattr(fetch_uniprot.cmd, "read_molstr", lambda *a, **k: None, False)
    assert fetch_uniprot.fetch_uniprot_ligands("p00918", verbose=False) == ["AZM"]
