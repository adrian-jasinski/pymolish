"""Tests for ``pymolish.extensions.structure.fetch_uniprot``."""

from __future__ import annotations

import sys
from unittest.mock import MagicMock

from pymolish.extensions.structure.fetch_uniprot import (
    fetch_by_uniprot,
    list_uniprot_structures,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _block_requests(monkeypatch):
    """Make ``import requests`` raise ImportError."""
    monkeypatch.setitem(sys.modules, "requests", None)


def _mock_requests(pdb_ids: list[str]):
    """Return a MagicMock for the requests module whose .post/.get returns pdb_ids."""
    mock_requests = MagicMock()
    payload = {
        "data": {"polymer_entities": [{"entry": {"id": pid}} for pid in pdb_ids]}
    }
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = payload
    mock_requests.post.return_value = mock_resp
    mock_requests.get.return_value = mock_resp
    return mock_requests


# ---------------------------------------------------------------------------
# Graceful degradation: requests missing
# ---------------------------------------------------------------------------


def test_fetch_by_uniprot_no_requests(pymol_cmd, monkeypatch, capsys):
    _block_requests(monkeypatch)
    result = fetch_by_uniprot("P04637")
    assert result == []
    assert "pymolish[biopython]" in capsys.readouterr().out


def test_list_uniprot_structures_no_requests(pymol_cmd, monkeypatch, capsys):
    _block_requests(monkeypatch)
    result = list_uniprot_structures("P04637")
    assert result == []
    assert "pymolish[biopython]" in capsys.readouterr().out


# ---------------------------------------------------------------------------
# fetch_by_uniprot
# ---------------------------------------------------------------------------


def test_fetch_by_uniprot_empty_id_returns_empty(pymol_cmd, monkeypatch, capsys):
    monkeypatch.setitem(sys.modules, "requests", MagicMock())
    result = fetch_by_uniprot("", verbose=False)
    assert result == []
    assert "non-empty" in capsys.readouterr().out


def test_fetch_by_uniprot_no_structures_found(pymol_cmd, monkeypatch, capsys):
    mock_req = MagicMock()
    # All searchers return empty / raise
    mock_resp = MagicMock()
    mock_resp.status_code = 404
    mock_req.post.return_value = mock_resp
    mock_req.get.return_value = mock_resp
    monkeypatch.setitem(sys.modules, "requests", mock_req)
    # Biopython also absent
    monkeypatch.setitem(sys.modules, "Bio", None)
    monkeypatch.setitem(sys.modules, "Bio.ExPASy", None)
    monkeypatch.setitem(sys.modules, "Bio.SwissProt", None)

    result = fetch_by_uniprot("ZZZZZZ", verbose=False)
    assert result == []
    assert "no pdb structures" in capsys.readouterr().out.lower()


def test_fetch_by_uniprot_happy(pymol_cmd, monkeypatch):
    mock_req = _mock_requests(["1TUP", "2OCJ"])
    monkeypatch.setitem(sys.modules, "requests", mock_req)

    result = fetch_by_uniprot("P04637", max_structures=10, verbose=False)
    assert "1TUP" in result or "2OCJ" in result
    assert pymol_cmd.fetch.call_count == len(result)


def test_fetch_by_uniprot_max_structures_limits_results(pymol_cmd, monkeypatch):
    mock_req = _mock_requests(["A000", "B001", "C002", "D003", "E004"])
    monkeypatch.setitem(sys.modules, "requests", mock_req)

    result = fetch_by_uniprot("P04637", max_structures=2, verbose=False)
    assert len(result) <= 2


def test_fetch_by_uniprot_handles_fetch_error(pymol_cmd, monkeypatch, capsys):
    mock_req = _mock_requests(["1TUP"])
    monkeypatch.setitem(sys.modules, "requests", mock_req)
    pymol_cmd.fetch.side_effect = Exception("network error")

    result = fetch_by_uniprot("P04637", verbose=True)
    assert result == []
    assert "failed" in capsys.readouterr().out.lower()


def test_fetch_by_uniprot_upcases_id(pymol_cmd, monkeypatch):
    mock_req = _mock_requests(["1TUP"])
    monkeypatch.setitem(sys.modules, "requests", mock_req)
    result = fetch_by_uniprot("p04637", max_structures=10, verbose=False)
    # The fetch call's object name should use the uppercased ID
    if result:
        obj_name = pymol_cmd.fetch.call_args_list[0].args[1]
        assert obj_name.startswith("P04637")


# ---------------------------------------------------------------------------
# list_uniprot_structures
# ---------------------------------------------------------------------------


def test_list_uniprot_structures_empty_id(pymol_cmd, monkeypatch, capsys):
    monkeypatch.setitem(sys.modules, "requests", MagicMock())
    result = list_uniprot_structures("", show_details=False)
    assert result == []
    assert "non-empty" in capsys.readouterr().out


def test_list_uniprot_structures_returns_ids(pymol_cmd, monkeypatch, capsys):
    mock_req = _mock_requests(["1TUP", "2OCJ"])
    # Details endpoint also mocked
    detail_resp = MagicMock()
    detail_resp.status_code = 200
    detail_resp.json.return_value = {
        "struct": {"title": "Test protein"},
        "rcsb_entry_info": {"resolution_combined": 2.1},
        "exptl": [{"method": "X-RAY"}],
    }
    mock_req.get.return_value = detail_resp
    # post (GraphQL) returns the list
    graphql_resp = MagicMock()
    graphql_resp.status_code = 200
    graphql_resp.json.return_value = {
        "data": {
            "polymer_entities": [
                {"entry": {"id": "1TUP"}},
                {"entry": {"id": "2OCJ"}},
            ]
        }
    }
    mock_req.post.return_value = graphql_resp
    monkeypatch.setitem(sys.modules, "requests", mock_req)

    result = list_uniprot_structures("P04637", show_details=False)
    assert "1TUP" in result or "2OCJ" in result
    out = capsys.readouterr().out
    assert "found" in out.lower()


def test_list_uniprot_structures_no_fetch_call(pymol_cmd, monkeypatch):
    mock_req = _mock_requests(["1TUP"])
    mock_req.get.return_value = MagicMock(
        status_code=200,
        json=lambda: {"struct": {"title": "t"}, "rcsb_entry_info": {}, "exptl": [{}]},
    )
    graphql_resp = MagicMock()
    graphql_resp.status_code = 200
    graphql_resp.json.return_value = {
        "data": {"polymer_entities": [{"entry": {"id": "1TUP"}}]}
    }
    mock_req.post.return_value = graphql_resp
    monkeypatch.setitem(sys.modules, "requests", mock_req)

    list_uniprot_structures("P04637", show_details=False)
    pymol_cmd.fetch.assert_not_called()
