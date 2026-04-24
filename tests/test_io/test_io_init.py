"""Tests for the I/O extension sub-package bootstrap."""

from __future__ import annotations

from pymolish.core.registry import CommandRegistry
from pymolish.extensions.io import __init_plugin__


def test_init_plugin_registers_all_io_commands(pymol_cmd):
    __init_plugin__(None)
    registry = CommandRegistry.instance()
    for name in (
        "load_files",
        "load_recursive",
        "list_loadable_files",
        "export_group",
        "export_objects",
        "export_by_pattern",
        "export_byres_to_csv",
    ):
        info = registry.get(name)
        assert info is not None, f"{name} should be registered"
        assert info.category == "I/O"
        assert info.examples  # every I/O command ships with examples


def test_init_plugin_registers_autocompletion(pymol_cmd):
    __init_plugin__(None)
    # After applying, auto_arg slot 0 should include load_files, export_group, etc.
    from pymolish.core.autocompletion import AutocompletionRegistry

    AutocompletionRegistry.instance().apply()
    commands_at_slot_0 = set(pymol_cmd.auto_arg[0].keys())
    assert {"load_files", "export_group", "export_byres_to_csv"} <= commands_at_slot_0
