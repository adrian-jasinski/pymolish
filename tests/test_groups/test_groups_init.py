"""Tests for the Groups extension sub-package bootstrap."""

from __future__ import annotations

from pymolish.core.registry import CommandRegistry
from pymolish.extensions.groups import __init_plugin__

_ALL_COMMANDS = [
    # toggle
    "group_enable",
    "group_disable",
    "group_toggle",
    "group_status",
    # navigate
    "group_next",
    "group_previous",
    # sort
    "sort_group_objects",
    "sort_all_groups",
    "group_info",
    "create_sorted_group",
    # copy
    "copy_group",
    "copy_group_objects",
    "list_group_copies",
    # merge
    "merge_to_group",
    "merge_to_objects",
    "list_merged_objects",
    # extract_chain
    "extract_chain_from_group",
    "extract_chains_from_group",
]


def test_init_plugin_registers_all_group_commands(pymol_cmd):
    __init_plugin__(None)
    registry = CommandRegistry.instance()

    for name in _ALL_COMMANDS:
        info = registry.get(name)
        assert info is not None, f"{name!r} should be registered"
        assert info.category == "Groups", f"{name!r} has wrong category"
        assert info.examples, f"{name!r} is missing examples"
        assert info.tags, f"{name!r} is missing tags"
        assert info.see_also, f"{name!r} is missing see_also"


def test_init_plugin_registers_autocompletion(pymol_cmd):
    __init_plugin__(None)
    from pymolish.core.autocompletion import AutocompletionRegistry

    AutocompletionRegistry.instance().apply()

    # Slot 0 should have completions for the key group commands
    commands_at_slot_0 = set(pymol_cmd.auto_arg[0].keys())
    expected = {
        "group_enable",
        "group_disable",
        "group_toggle",
        "group_status",
        "group_next",
        "group_previous",
        "sort_group_objects",
        "group_info",
        "create_sorted_group",
        "copy_group",
        "copy_group_objects",
        "list_group_copies",
        "merge_to_group",
        "merge_to_objects",
        "list_merged_objects",
        "extract_chain_from_group",
        "extract_chains_from_group",
    }
    assert expected <= commands_at_slot_0


def test_init_plugin_multi_arg_autocompletion(pymol_cmd):
    """merge_to_group and merge_to_objects register slot-1 completions."""
    __init_plugin__(None)
    from pymolish.core.autocompletion import AutocompletionRegistry

    AutocompletionRegistry.instance().apply()

    # auto_arg has at least 2 slots after apply
    assert len(pymol_cmd.auto_arg) >= 2
    commands_at_slot_1 = set(pymol_cmd.auto_arg[1].keys())
    assert "merge_to_group" in commands_at_slot_1
    assert "merge_to_objects" in commands_at_slot_1


def test_init_plugin_is_idempotent_with_registry_reset(pymol_cmd):
    """Calling __init_plugin__ after a registry reset should not raise."""
    __init_plugin__(None)
    CommandRegistry._reset_for_tests()
    from pymolish.core.autocompletion import AutocompletionRegistry

    AutocompletionRegistry._reset_for_tests()

    # Second run (fresh registry) should succeed
    __init_plugin__(None)
    registry = CommandRegistry.instance()
    assert registry.get("group_enable") is not None
