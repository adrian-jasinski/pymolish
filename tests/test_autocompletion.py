"""Smoke tests for ``pymolish.core.autocompletion``."""

from __future__ import annotations

import pytest

from pymolish.core.autocompletion import AutocompletionRegistry


def test_singleton_returns_same_instance():
    ar = AutocompletionRegistry.instance()
    assert ar is AutocompletionRegistry.instance()


def test_register_queues_completion_entry():
    ar = AutocompletionRegistry.instance()
    ar.register("load_files", 0, lambda t: ["foo/"], label="directory")
    entries = ar.entries()
    assert len(entries) == 1
    assert entries[0].command == "load_files"
    assert entries[0].position == 0
    assert entries[0].label == "directory"


def test_apply_populates_cmd_auto_arg(pymol_cmd):
    ar = AutocompletionRegistry.instance()
    completer = lambda t: ["pdb", "cif"]  # noqa: E731
    ar.register("load_files", 1, completer, label="suffix")
    ar.apply()

    slot = pymol_cmd.auto_arg[1]
    assert "load_files" in slot
    assert slot["load_files"][0] is completer
    assert slot["load_files"][1] == "suffix"


def test_subclassing_is_rejected():
    with pytest.raises(TypeError):

        class _Bad(AutocompletionRegistry):  # noqa: D401
            """Should never instantiate."""
