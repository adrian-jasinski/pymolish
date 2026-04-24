"""Smoke tests for ``pymolish.core.logging``."""

from __future__ import annotations

from pymolish.core.logging import plog


def test_plog_info_uses_prefix(capsys):
    plog("io", "hello world")
    captured = capsys.readouterr().out.strip()
    assert captured == "[pext:io] hello world"


def test_plog_warn_includes_warning_label(capsys):
    plog("groups", "watch out", "warn")
    assert "WARNING: watch out" in capsys.readouterr().out


def test_plog_error_includes_error_label(capsys):
    plog("registry", "boom", "error")
    assert "ERROR: boom" in capsys.readouterr().out
