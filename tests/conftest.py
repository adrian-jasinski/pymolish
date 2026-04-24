"""Shared pytest fixtures and PyMOL mocks for the pymolish test suite."""

from __future__ import annotations

import sys
from types import ModuleType
from unittest.mock import MagicMock

import pytest


def _install_pymol_mock() -> None:
    """Insert a ``pymol`` mock hierarchy into :mod:`sys.modules` if absent.

    Runs at import time so every test module can freely ``import pymol.cmd``.
    """
    if "pymol" in sys.modules and not isinstance(sys.modules["pymol"], _PyMOLMock):
        # Real pymol is available (e.g. running inside PyMOL); leave it alone.
        return

    pymol_mod = _PyMOLMock("pymol")
    cmd_mock = MagicMock(name="pymol.cmd")
    cmd_mock.get_names.return_value = []
    cmd_mock.get_object_list.return_value = []
    cmd_mock.get_type.return_value = ""
    cmd_mock.count_atoms.return_value = 0
    cmd_mock.auto_arg = [{}, {}, {}, {}]
    pymol_mod.cmd = cmd_mock

    plugins_mock = MagicMock(name="pymol.plugins")
    pymol_mod.plugins = plugins_mock

    qt_mock = MagicMock(name="pymol.Qt")
    pymol_mod.Qt = qt_mock

    sys.modules["pymol"] = pymol_mod
    sys.modules["pymol.cmd"] = cmd_mock
    sys.modules["pymol.plugins"] = plugins_mock
    sys.modules["pymol.Qt"] = qt_mock


class _PyMOLMock(ModuleType):
    """Marker subclass so we can detect our own mock vs. a real install."""


_install_pymol_mock()


_CMD_ATTRS_TO_RESET = (
    "get_names",
    "get_object_list",
    "get_type",
    "count_atoms",
    "load",
    "save",
    "group",
    "iterate",
    "delete",
    "extend",
)


@pytest.fixture
def pymol_cmd():
    """Yield the mocked ``pymol.cmd`` with per-call state reset between tests."""
    cmd = sys.modules["pymol"].cmd
    cmd.reset_mock(return_value=True, side_effect=True)
    for attr in _CMD_ATTRS_TO_RESET:
        getattr(cmd, attr).reset_mock(return_value=True, side_effect=True)
    cmd.get_names.return_value = []
    cmd.get_object_list.return_value = []
    cmd.get_type.return_value = ""
    cmd.count_atoms.return_value = 0
    cmd.auto_arg = [{}, {}, {}, {}]
    yield cmd


@pytest.fixture(autouse=True)
def _reset_registries():
    """Reset pymolish singletons between tests so state does not leak."""
    from pymolish.core.autocompletion import AutocompletionRegistry
    from pymolish.core.registry import CommandRegistry

    CommandRegistry._reset_for_tests()
    AutocompletionRegistry._reset_for_tests()
    yield
    CommandRegistry._reset_for_tests()
    AutocompletionRegistry._reset_for_tests()
