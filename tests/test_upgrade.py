"""Tests for ``pymolish.core.upgrade``."""

from __future__ import annotations

import io
import json
import os
import zipfile

import pymolish
from pymolish.core import upgrade

_LISTING = [
    {"name": "pymolish.zip", "download_url": "u0"},
    {"name": "pymolish_0_1_9.zip", "download_url": "u9"},
    {"name": "pymolish_0_1_30.zip", "download_url": "u30"},
    {"name": "pymolish_0_1_31.zip", "download_url": "u31"},
]


def _fake_urlopen(zip_bytes: bytes):
    def urlopen(url, timeout=0):
        body = zip_bytes if url == "u31" else json.dumps(_LISTING).encode()
        return io.BytesIO(body)

    return urlopen


def _zip_with(version: str) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr("pymolish/__init__.py", "")
        z.writestr("pymolish/_version.py", f'__version__ = "{version}"\n')
    return buf.getvalue()


def _patch_zip(monkeypatch):
    monkeypatch.setattr(
        upgrade.urllib.request, "urlopen", _fake_urlopen(_zip_with("0.1.31"))
    )


def test_latest_release_picks_highest_versioned_zip(monkeypatch):
    monkeypatch.setattr(upgrade.urllib.request, "urlopen", _fake_urlopen(b""))
    assert upgrade._latest_release() == ((0, 1, 31), "u31")


def test_up_to_date_does_nothing(monkeypatch, capsys):
    monkeypatch.setattr(upgrade.urllib.request, "urlopen", _fake_urlopen(b""))
    monkeypatch.setattr(pymolish, "__version__", "0.1.31")
    assert upgrade.pymolish_upgrade() is None
    assert "already up to date" in capsys.readouterr().out


def test_check_only_reports_without_installing(monkeypatch, capsys):
    monkeypatch.setattr(upgrade.urllib.request, "urlopen", _fake_urlopen(b""))
    monkeypatch.setattr(pymolish, "__version__", "0.1.22")
    monkeypatch.setattr(upgrade, "_install", lambda *_: 1 / 0)
    assert upgrade.pymolish_upgrade(check_only=1) == "0.1.31"
    assert "run pymolish_upgrade" in capsys.readouterr().out


def test_refuses_dir_outside_plugin_path(monkeypatch, capsys):
    monkeypatch.setattr(upgrade.urllib.request, "urlopen", _fake_urlopen(b""))
    monkeypatch.setattr(pymolish, "__version__", "0.1.22")
    assert upgrade.pymolish_upgrade() == "0.1.31"
    assert "not a PyMOL plugin directory" in capsys.readouterr().out


def test_installs_and_respects_restart_no(monkeypatch, tmp_path, capsys):
    target = tmp_path / "startup" / "pymolish"
    target.mkdir(parents=True)
    (target / "old.py").write_text("")
    monkeypatch.setattr(upgrade, "_install_target", lambda: str(target))
    _patch_zip(monkeypatch)
    monkeypatch.setattr(pymolish, "__version__", "0.1.22")
    reloaded = []
    monkeypatch.setattr(upgrade, "pymolish_reload", lambda: reloaded.append(1))

    assert upgrade.pymolish_upgrade(restart=0) == "0.1.31"
    assert not reloaded
    assert not (target / "old.py").exists()
    assert "0.1.31" in (target / "_version.py").read_text()
    assert "run pymolish_reload" in capsys.readouterr().out


def test_dialog_yes_triggers_reload(monkeypatch, tmp_path):
    target = tmp_path / "pymolish"
    target.mkdir()
    monkeypatch.setattr(upgrade, "_install_target", lambda: str(target))
    _patch_zip(monkeypatch)
    monkeypatch.setattr(pymolish, "__version__", "0.1.22")
    monkeypatch.setattr(upgrade, "_ask_yes_no", lambda *_: True)
    reloaded = []
    monkeypatch.setattr(upgrade, "pymolish_reload", lambda: reloaded.append(1))
    upgrade.pymolish_upgrade()
    assert reloaded


def test_reload_reimports_and_registers(pymol_cmd):
    import sys

    saved = {k: v for k, v in sys.modules.items() if "pymolish" in k.split(".")}
    try:
        assert upgrade.pymolish_reload() == pymolish.__version__
        fresh = sys.modules["pymolish"]
        assert fresh is not pymolish
        assert "pymolish_upgrade" in fresh.core.registry.CommandRegistry.instance()
    finally:  # put the original module objects back so other tests see one world
        for k in [k for k in sys.modules if "pymolish" in k.split(".")]:
            del sys.modules[k]
        sys.modules.update(saved)
    assert os.path.basename(upgrade._PACKAGE_DIR) == "pymolish"
