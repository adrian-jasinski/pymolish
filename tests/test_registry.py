"""Smoke tests for ``pymolish.core.registry``."""

from __future__ import annotations

import pytest

from pymolish.core.registry import CommandInfo, CommandRegistry
from pymolish.core.types import Category


def _sample(x: int = 1, y: str = "z") -> int:
    """Example command used as a registration target."""
    return x


def test_singleton_returns_same_instance():
    registry = CommandRegistry.instance()
    assert registry is CommandRegistry.instance()


def test_register_stores_info_and_extends_pymol(pymol_cmd):
    registry = CommandRegistry.instance()
    info = registry.register(
        "sample",
        _sample,
        category=Category.IO,
        description="sample command",
        examples=["sample 1, z"],
        tags=["demo"],
    )

    assert isinstance(info, CommandInfo)
    assert info.name == "sample"
    assert info.category == "I/O"
    assert "sample" in registry
    pymol_cmd.extend.assert_called_once_with("sample", _sample)


def test_duplicate_registration_rejected(pymol_cmd):
    registry = CommandRegistry.instance()
    registry.register("sample", _sample, category=Category.IO, description="x")
    with pytest.raises(ValueError):
        registry.register("sample", _sample, category=Category.IO, description="x")


def test_list_commands_filters_by_category(pymol_cmd):
    registry = CommandRegistry.instance()
    registry.register("a", _sample, category=Category.IO, description="a")
    registry.register("b", _sample, category=Category.GROUPS, description="b")

    io_only = registry.list_commands(Category.IO)
    assert [info.name for info in io_only] == ["a"]
    assert registry.categories() == ["Groups", "I/O"]


def test_search_matches_name_description_and_tags(pymol_cmd):
    registry = CommandRegistry.instance()
    registry.register(
        "load_files",
        _sample,
        category=Category.IO,
        description="load batch",
        tags=["batch", "files"],
    )
    registry.register(
        "color_group",
        _sample,
        category=Category.VISUALIZATION,
        description="color a group",
        tags=["palette"],
    )

    assert [i.name for i in registry.search("batch")] == ["load_files"]
    assert [i.name for i in registry.search("group")] == ["color_group"]
    assert registry.search("") == []


def test_subclassing_is_rejected():
    with pytest.raises(TypeError):

        class _Bad(CommandRegistry):  # noqa: D401
            """Should never instantiate."""


def test_usage_inference_includes_defaults(pymol_cmd):
    registry = CommandRegistry.instance()
    info = registry.register(
        "sample",
        _sample,
        category=Category.IO,
        description="demo",
    )
    assert info.usage.startswith("sample ")
    assert "x=1" in info.usage
