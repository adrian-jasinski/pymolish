"""Tests for the Visualization extension sub-package bootstrap."""

from __future__ import annotations

from pymolish.core.registry import CommandRegistry
from pymolish.extensions.visualization import __init_plugin__

_EXPECTED_COMMANDS = (
    "register_extended_colors",
    "list_available_palettes",
    "color_group_with_palette",
    "color_group_with_gradient",
    "color_secondary_structure",
    "list_cartoon_palettes",
)


def test_init_plugin_registers_all_visualization_commands(pymol_cmd):
    __init_plugin__(None)
    registry = CommandRegistry.instance()
    for name in _EXPECTED_COMMANDS:
        info = registry.get(name)
        assert info is not None, f"'{name}' should be registered"
        assert info.category == "Visualization", f"'{name}' has wrong category"
        assert info.examples, f"'{name}' must have at least one example"


def test_init_plugin_can_be_called_without_app(pymol_cmd):
    """Calling __init_plugin__ with no argument should not raise."""
    __init_plugin__()


def test_init_plugin_registers_autocompletion_slots(pymol_cmd):
    __init_plugin__(None)

    from pymolish.core.autocompletion import AutocompletionRegistry

    AutocompletionRegistry.instance().apply()
    commands_at_slot_0 = set(pymol_cmd.auto_arg[0].keys())
    assert {
        "register_extended_colors",
        "color_group_with_palette",
        "color_group_with_gradient",
        "color_secondary_structure",
    } <= commands_at_slot_0


def test_palette_completer_returns_palette_names(pymol_cmd):
    """Slot-1 completer for color_group_with_palette should return palette names."""
    __init_plugin__(None)

    from pymolish.core.autocompletion import AutocompletionRegistry

    AutocompletionRegistry.instance().apply()
    completer_entry = pymol_cmd.auto_arg[1].get("color_group_with_palette")
    assert completer_entry is not None
    completer_fn = completer_entry[0]
    results = completer_fn("")
    assert "pastels" in results
    assert "neon" in results


def test_cartoon_palette_completer_filters_by_prefix(pymol_cmd):
    __init_plugin__(None)

    from pymolish.core.autocompletion import AutocompletionRegistry

    AutocompletionRegistry.instance().apply()
    completer_entry = pymol_cmd.auto_arg[1].get("color_secondary_structure")
    assert completer_entry is not None
    completer_fn = completer_entry[0]
    results = completer_fn("ard")
    assert "ard" in results
    assert "ard_green" in results
    # Should not include palettes that don't start with "ard"
    assert "sunset" not in results
