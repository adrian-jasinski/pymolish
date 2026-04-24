"""Shared PyQt GUI infrastructure.

Importing this package must succeed even when PyQt5 is not installed. Concrete
dialog classes live in :mod:`pymolish.gui.base_dialog` and gate their imports
behind runtime checks.
"""

from .base_dialog import HAS_QT, BaseExtensionDialog

__all__ = ["HAS_QT", "BaseExtensionDialog"]
