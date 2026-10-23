"""Tests for ``pymolish.core.deps.pymolish_install_deps``."""

from __future__ import annotations

import subprocess

from pymolish.core import deps


def _fake_run(calls, *, has_pymol=True, has_pip=True, install_ok=True):
    def run(command, **_):
        calls.append(command)
        if command[1:] == ["-c", "import pymol"]:
            code = 0 if has_pymol else 1
        elif command[1:] == ["-m", "pip", "--version"]:
            code = 0 if has_pip else 1
        else:
            code = 0 if install_ok else 1
        return subprocess.CompletedProcess(command, code, stdout="", stderr="boom")

    return run


def _setup(monkeypatch, calls, installed=(), **kwargs):
    monkeypatch.setattr(deps, "_pymol_python", lambda: "/env/bin/python")
    monkeypatch.setattr(deps, "_is_installed", lambda module: module in installed)
    monkeypatch.setattr(deps.subprocess, "run", _fake_run(calls, **kwargs))


def test_installs_only_missing_with_pip(monkeypatch):
    calls = []
    _setup(monkeypatch, calls, installed=("numpy",))
    result = deps.pymolish_install_deps("numpy, biopython")
    assert result == ["biopython>=1.83"]
    assert calls[-1] == ["/env/bin/python", "-m", "pip", "install", "biopython>=1.83"]


def test_falls_back_to_uv_without_pip(monkeypatch):
    calls = []
    _setup(monkeypatch, calls, has_pip=False)
    monkeypatch.setattr(deps.shutil, "which", lambda _: "/usr/bin/uv")
    deps.pymolish_install_deps("biopython")
    assert calls[-1][:5] == [
        "/usr/bin/uv",
        "pip",
        "install",
        "--python",
        "/env/bin/python",
    ]


def test_refuses_when_python_cannot_import_pymol(monkeypatch, capsys):
    calls = []
    _setup(monkeypatch, calls, has_pymol=False)
    assert deps.pymolish_install_deps("all") == []
    assert "wrong environment" in capsys.readouterr().out
    assert len(calls) == 1


def test_dry_run_does_not_install(monkeypatch, capsys):
    calls = []
    _setup(monkeypatch, calls)
    result = deps.pymolish_install_deps("all", dry_run="1")
    assert result == ["numpy>=1.20", "matplotlib>=3.3", "biopython>=1.83"]
    assert not any("install" in c for c in calls)
    assert "would run" in capsys.readouterr().out


def test_unknown_extra_and_failed_install(monkeypatch, capsys):
    calls = []
    _setup(monkeypatch, calls, install_ok=False)
    assert deps.pymolish_install_deps("nope") == []
    assert "unknown extra" in capsys.readouterr().out
    assert deps.pymolish_install_deps("numpy") == []
    assert "install failed" in capsys.readouterr().out
