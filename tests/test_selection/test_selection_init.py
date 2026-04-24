"""Tests for the Selection extension sub-package bootstrap."""

from __future__ import annotations

from pymolish.core.registry import CommandRegistry
from pymolish.extensions.selection import __init_plugin__


def test_init_plugin_registers_search_sequence(pymol_cmd):
    __init_plugin__(None)
    registry = CommandRegistry.instance()

    info = registry.get("search_sequence")
    assert info is not None, "search_sequence should be registered"
    assert info.category == "Selection"
    assert info.examples


def test_init_plugin_registers_autocompletion(pymol_cmd):
    __init_plugin__(None)

    from pymolish.core.autocompletion import AutocompletionRegistry

    AutocompletionRegistry.instance().apply()
    commands_at_slot_0 = set(pymol_cmd.auto_arg[0].keys())
    assert "search_sequence" in commands_at_slot_0
