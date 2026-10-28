"""Tests for ``pymolish.extensions.groups._menu``."""

from __future__ import annotations

import sys
from types import ModuleType

import pytest

from pymolish.extensions.groups import _menu


@pytest.fixture
def fake_menu(monkeypatch):
    menu = ModuleType("pymol.menu")
    rows = [[1, f"row{i}", f"cmd{i}"] for i in range(10)]
    rows[5] = [1, r"\933delete group", "cmd5"]
    menu.group_action = lambda self_cmd, sele: list(rows)
    monkeypatch.setitem(sys.modules, "pymol.menu", menu)
    monkeypatch.setattr(sys.modules["pymol"], "menu", menu, raising=False)
    return menu


def test_install_wraps_group_action(fake_menu, pymol_cmd):
    assert _menu.install() is True
    rows = fake_menu.group_action(None, "g")
    labels = [r[1] for r in rows]
    # inserted directly before PyMOL's "delete group" row, which stays last
    assert labels[5] == _menu.BLUE + "duplicate group"
    assert labels[8] == _menu.BLUE + "disable group"
    assert labels[9] == r"\933delete group"
    assert labels[-4:] == ["row6", "row7", "row8", "row9"]
    assert [1, _menu.BLUE + "duplicate group", "copy_group g"] in rows
    assert [1, _menu.BLUE + "enable group", "group_enable g"] in rows
    assert [1, _menu.BLUE + "disable group", "group_disable g"] in rows


def test_install_is_idempotent(fake_menu, pymol_cmd):
    _menu.install()
    first = fake_menu.group_action
    assert _menu.install() is True
    assert fake_menu.group_action is first
    expected = 10 + len(_menu.pymolish_group_items("g"))
    assert len(fake_menu.group_action(None, "g")) == expected


def test_sort_entry_flips_direction(pymol_cmd):
    pymol_cmd.get_type.return_value = "object:group"
    pymol_cmd.get_object_list.return_value = ["a", "b", "c"]
    assert _menu._sort_entry("g") == [
        1,
        _menu.BLUE + "sort group",
        "sort_group g, reverse=1",
    ]

    pymol_cmd.get_object_list.return_value = ["c", "b", "a"]
    assert _menu._sort_entry("g") == [
        1,
        _menu.BLUE + "sort group",
        "sort_group g, reverse=0",
    ]


def test_install_without_pymol_menu(monkeypatch):
    monkeypatch.delitem(sys.modules, "pymol.menu", raising=False)
    monkeypatch.delattr(sys.modules["pymol"], "menu", raising=False)
    # plain module object with no 'menu' attribute -> ImportError path
    assert _menu.install() is False


def test_menu_labels_are_ascii(pymol_cmd):
    for row in _menu.pymolish_group_items("g"):
        assert row[1].isascii(), row[1]
