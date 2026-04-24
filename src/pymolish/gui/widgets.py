"""Reusable PyQt widgets for pymolish extension dialogs.

Phase 4 populates this module with widgets like ``GroupPickerCombo`` and
``FileBrowserLineEdit``. For now it exposes the optional-dependency guard so
unit tests can import the module without PyQt5 installed.
"""

from __future__ import annotations

from .base_dialog import HAS_QT

__all__ = ["HAS_QT"]
