"""Tests for the structure extension sub-package bootstrap."""

from __future__ import annotations

from pymolish.core.registry import CommandRegistry
from pymolish.extensions.structure import __init_plugin__

_EXPECTED_COMMANDS = (
    "multialign",
    "list_objects_with_prefix",
    "remove_ions",
    "remove_metals",
    "cluster_ligands_by_position",
    "cluster_ligands_from_group",
    "fetch_by_uniprot",
    "list_uniprot_structures",
)


def test_init_plugin_registers_all_structure_commands(pymol_cmd):
    __init_plugin__(None)
    registry = CommandRegistry.instance()
    for name in _EXPECTED_COMMANDS:
        info = registry.get(name)
        assert info is not None, f"{name!r} should be registered"
        assert info.category == "Structure", (
            f"{name!r} has category {info.category!r}, expected 'Structure'"
        )
        assert info.examples, f"{name!r} must ship with at least one example"
        assert info.tags, f"{name!r} must have tags"
        assert info.see_also, f"{name!r} must have see_also"


def test_init_plugin_is_idempotent_category(pymol_cmd):
    """All registered commands belong to the Structure category."""
    __init_plugin__(None)
    registry = CommandRegistry.instance()
    structure_commands = registry.list_commands(category="Structure")
    names = {info.name for info in structure_commands}
    for expected in _EXPECTED_COMMANDS:
        assert expected in names


def test_init_plugin_registers_autocompletion(pymol_cmd):
    __init_plugin__(None)
    from pymolish.core.autocompletion import AutocompletionRegistry

    ac = AutocompletionRegistry.instance()
    ac.apply()

    # Slot 0 should include commands that take a group/object as first arg
    commands_at_slot_0 = set(pymol_cmd.auto_arg[0].keys())
    assert {"multialign", "remove_ions", "remove_metals"} <= commands_at_slot_0

    # Slot 1 should include multialign (target = second arg)
    commands_at_slot_1 = set(pymol_cmd.auto_arg[1].keys())
    assert "multialign" in commands_at_slot_1
