"""Scale the PyMOL Qt interface fonts and panels for recording or presenting."""

from __future__ import annotations

from pymol import cmd

from ...core.cli import clean as _clean
from ...core.logging import plog

_TAG = "viz.ui_scale"

_PANEL_SETTINGS = (
    "display_scale_factor",
    "internal_gui_control_size",
    "internal_gui_width",
)

# Snapshot of the pristine state, captured on the first ui_scale call.
_original: dict[str, object] = {}

_STYLE = """
QMenuBar, QMenu, QDockWidget, QTreeWidget, QListWidget, QPushButton, QToolButton,
QLineEdit, QPlainTextEdit, QComboBox, QLabel, QTabBar::tab {{ font-size: {pt}pt; }}
QMenu::item {{ padding: 6px 28px 6px 22px; }}
QPushButton, QToolButton {{ min-height: {pt2}px; padding: 3px 7px; }}
QTreeWidget::item, QListWidget::item {{ min-height: {pt2}px; }}
QTabBar::tab {{ padding: 6px 10px; }}
"""


def _qt_app():
    try:
        from pymol.Qt import QtWidgets
    except ImportError:
        return None
    return QtWidgets.QApplication.instance()


def _snapshot() -> None:
    if _original:
        return
    for name in _PANEL_SETTINGS:
        _original[name] = cmd.get(name)
    app = _qt_app()
    if app is not None:
        _original["font"] = app.font()
        _original["stylesheet"] = app.styleSheet()


def ui_scale(
    font_size: int | str = 14,
    scale_factor: int | str = "",
    control_size: int | str = "",
    panel_width: int | str = "",
) -> dict[str, object]:
    """Enlarge PyMOL's Qt interface (menus, command line, output, buttons, panel).

    One knob (``font_size``) drives everything; the right-hand object panel
    values are derived from it unless given explicitly. Call
    :func:`ui_scale_reset` to restore the original look.

    Args:
        font_size: Point size for all Qt widgets. Default: ``14``.
        scale_factor: ``display_scale_factor`` for the internal (OpenGL) GUI.
            Default: ``2`` when ``font_size`` > 12, else ``1``.
        control_size: ``internal_gui_control_size`` (object panel button
            height). Default: ``font_size * 1.5``.
        panel_width: ``internal_gui_width`` in pixels. Default: ``font_size * 18``.

    Returns:
        Dict of the values applied: ``font_size``, ``display_scale_factor``,
        ``internal_gui_control_size``, ``internal_gui_width``, and ``qt`` (bool,
        whether a Qt application was found and styled).

    Examples:
        PyMOL> ui_scale
        PyMOL> ui_scale 16
        PyMOL> ui_scale 14, 2, 22, 250

    Since:
        0.1.19

    See Also:
        ui_scale_reset
    """
    pt = int(_clean(str(font_size)))
    sf = int(_clean(str(scale_factor)) or (2 if pt > 12 else 1))
    cs = int(_clean(str(control_size)) or round(pt * 1.5))
    pw = int(_clean(str(panel_width)) or pt * 18)

    _snapshot()

    cmd.set("display_scale_factor", sf)
    cmd.set("internal_gui_control_size", cs)
    cmd.set("internal_gui_width", pw)

    app = _qt_app()
    if app is not None:
        font = app.font()
        font.setPointSize(pt)
        app.setFont(font)
        app.setStyleSheet(_STYLE.format(pt=pt, pt2=pt * 2))
    else:
        plog(
            _TAG,
            "no Qt application found; only internal GUI settings applied",
            "warning",
        )

    plog(_TAG, f"font {pt}pt, scale {sf}, control {cs}, panel width {pw}")
    return {
        "font_size": pt,
        "display_scale_factor": sf,
        "internal_gui_control_size": cs,
        "internal_gui_width": pw,
        "qt": app is not None,
    }


def ui_scale_reset() -> bool:
    """Restore the interface sizes captured before the first :func:`ui_scale`.

    Returns:
        ``True`` when a previous :func:`ui_scale` state was restored, ``False``
        when there was nothing to reset.

    Examples:
        PyMOL> ui_scale_reset

    Since:
        0.1.19

    See Also:
        ui_scale
    """
    if not _original:
        plog(_TAG, "nothing to reset; ui_scale was not called")
        return False
    for name in _PANEL_SETTINGS:
        cmd.set(name, _original[name])
    app = _qt_app()
    if app is not None and "font" in _original:
        app.setFont(_original["font"])
        app.setStyleSheet(_original["stylesheet"])
    _original.clear()
    plog(_TAG, "interface sizes restored")
    return True
