"""End-to-end smoke test for ``pymolish.__init_plugin__``."""

from __future__ import annotations

import pymolish
from pymolish.core.registry import CommandRegistry


def test_init_plugin_registers_meta_commands(pymol_cmd):
    pymolish.__init_plugin__(None)
    registry = CommandRegistry.instance()
    for name in (
        "pymolish_list",
        "pymolish_help",
        "pymolish_search",
        "pymolish_categories",
        "pymolish_version",
    ):
        assert name in registry
        info = registry.get(name)
        assert info is not None
        assert info.category == "Meta"


def test_pymolish_version_prints_and_returns_version(pymol_cmd, capsys):
    assert pymolish.pymolish_version() == pymolish.__version__
    assert pymolish.__version__ in capsys.readouterr().out


def test_pymolish_search_returns_empty_on_miss(pymol_cmd, capsys):
    pymolish.__init_plugin__(None)
    result = pymolish.pymolish_search("zzz-not-a-real-term")
    assert result == []


def test_pymolish_categories_counts(pymol_cmd):
    pymolish.__init_plugin__(None)
    counts = pymolish.pymolish_categories()
    assert counts.get("Meta") == 5
