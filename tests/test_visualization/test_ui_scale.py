"""Tests for ``pymolish.extensions.visualization.ui_scale``."""

from __future__ import annotations

from unittest.mock import MagicMock

from pymolish.extensions.visualization import ui_scale as mod


def _fake_app(monkeypatch):
    app = MagicMock()
    app.font.return_value = MagicMock()
    app.styleSheet.return_value = ""
    monkeypatch.setattr(mod, "_qt_app", lambda: app)
    mod._original.clear()
    return app


def test_ui_scale_derives_panel_values_and_styles_qt(pymol_cmd, monkeypatch):
    app = _fake_app(monkeypatch)
    pymol_cmd.get.side_effect = lambda n: {"display_scale_factor": 1}.get(n, 18)

    result = mod.ui_scale("14")

    assert result == {
        "font_size": 14,
        "display_scale_factor": 2,
        "internal_gui_control_size": 21,
        "internal_gui_width": 252,
        "qt": True,
    }
    pymol_cmd.set.assert_any_call("internal_gui_width", 252)
    app.setFont.assert_called_once()
    assert "14pt" in app.setStyleSheet.call_args[0][0]


def test_ui_scale_explicit_overrides(pymol_cmd, monkeypatch):
    _fake_app(monkeypatch)
    result = mod.ui_scale(12, "2", "22", "250")
    assert result["display_scale_factor"] == 2
    assert result["internal_gui_control_size"] == 22
    assert result["internal_gui_width"] == 250


def test_ui_scale_reset_restores_snapshot(pymol_cmd, monkeypatch):
    app = _fake_app(monkeypatch)
    orig_font = app.font.return_value
    pymol_cmd.get.return_value = 7

    assert mod.ui_scale_reset() is False
    mod.ui_scale(16)
    pymol_cmd.set.reset_mock()

    assert mod.ui_scale_reset() is True
    for name in mod._PANEL_SETTINGS:
        pymol_cmd.set.assert_any_call(name, 7)
    app.setFont.assert_called_with(orig_font)
    app.setStyleSheet.assert_called_with("")
    assert mod._original == {}
