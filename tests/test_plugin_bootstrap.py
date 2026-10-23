"""End-to-end smoke test for ``pymolish.__init_plugin__``."""

from __future__ import annotations

import pymolish
from pymolish.core.autocompletion import AutocompletionRegistry
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
    assert counts == {
        "Groups": 18,
        "I/O": 7,
        "Meta": 6,
        "Selection": 1,
        "Structure": 8,
        "Visualization": 6,
    }


def test_animation_commands_are_removed(pymol_cmd, capsys):
    pymolish.__init_plugin__(None)
    registry = CommandRegistry.instance()
    removed = {
        "fade_in",
        "fade_out",
        "movie_from_group",
        "movie_transparency",
        "set_frame_transparency",
        "suggest_transparency_type",
        "transparency_pulse",
        "transparency_range",
        "transparency_sequence",
    }

    names = pymolish.pymolish_list()
    assert len(names) == 46
    assert removed.isdisjoint(names)
    assert "== Animation ==" not in capsys.readouterr().out
    assert registry.list_commands("Animation") == []
    assert pymolish.pymolish_list("Animation") == []
    assert pymolish.pymolish_search("animation") == []
    for name in removed:
        assert registry.get(name) is None
        assert pymolish.pymolish_search(name) == []
        assert pymolish.pymolish_help(name) is None

    extended = {call.args[0] for call in pymol_cmd.extend.call_args_list}
    assert removed.isdisjoint(extended)
    completions = AutocompletionRegistry.instance().entries()
    assert removed.isdisjoint(entry.command for entry in completions)
    for slot in pymol_cmd.auto_arg:
        assert removed.isdisjoint(slot)

    pymolish.pymolish_version()
    assert "(46 commands loaded)" in capsys.readouterr().out


def test_pymolish_list_self_heals_when_only_meta_registered(pymol_cmd, monkeypatch):
    """If extensions were never bootstrapped, listing triggers it lazily."""
    monkeypatch.setattr(pymolish, "_extensions_loaded", False)
    pymolish._register_meta_commands()
    registry = CommandRegistry.instance()
    assert registry.categories() == ["Meta"]

    names = pymolish.pymolish_list()

    assert len(names) > 5
    assert set(registry.categories()) > {"Meta"}
    assert "load_files" in registry
