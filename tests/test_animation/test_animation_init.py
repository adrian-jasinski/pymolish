"""Tests for the animation extension sub-package bootstrap."""

from __future__ import annotations

from pymolish.core.autocompletion import AutocompletionRegistry
from pymolish.core.registry import CommandRegistry
from pymolish.extensions.animation import __init_plugin__

_ALL_COMMANDS = (
    "movie_transparency",
    "fade_in",
    "fade_out",
    "transparency_pulse",
    "suggest_transparency_type",
    "set_frame_transparency",
    "transparency_sequence",
    "transparency_range",
    "movie_from_group",
)


def test_init_plugin_registers_all_animation_commands(pymol_cmd):
    __init_plugin__(None)
    registry = CommandRegistry.instance()
    for name in _ALL_COMMANDS:
        info = registry.get(name)
        assert info is not None, f"{name} should be registered"
        assert info.category == "Animation"
        assert info.examples, f"{name} must have examples"


def test_init_plugin_is_idempotent_when_called_once(pymol_cmd):
    """Calling __init_plugin__ once must not raise."""
    __init_plugin__(None)
    registry = CommandRegistry.instance()
    assert len(registry.list_commands()) == len(_ALL_COMMANDS)


def test_init_plugin_all_commands_have_see_also(pymol_cmd):
    __init_plugin__(None)
    registry = CommandRegistry.instance()
    for name in _ALL_COMMANDS:
        info = registry.get(name)
        assert info.see_also, f"{name} must declare see_also"


def test_init_plugin_all_commands_have_tags(pymol_cmd):
    __init_plugin__(None)
    registry = CommandRegistry.instance()
    for name in _ALL_COMMANDS:
        info = registry.get(name)
        assert info.tags, f"{name} must have tags"


def test_init_plugin_registers_autocompletion(pymol_cmd):
    __init_plugin__(None)
    AutocompletionRegistry.instance().apply()
    commands_at_slot_0 = set(pymol_cmd.auto_arg[0].keys())
    expected = {
        "movie_transparency",
        "fade_in",
        "fade_out",
        "transparency_pulse",
        "suggest_transparency_type",
        "set_frame_transparency",
        "transparency_sequence",
        "transparency_range",
        "movie_from_group",
    }
    assert expected <= commands_at_slot_0
