"""Base class for pymolish PyQt dialogs.

Importable without PyQt5 installed — :data:`HAS_QT` reports availability.
Concrete dialog widgets should subclass :class:`BaseExtensionDialog` only when
``HAS_QT`` is ``True``.
"""

from __future__ import annotations

try:
    from pymol.Qt import QtWidgets  # type: ignore[import-not-found]

    HAS_QT = True
except ImportError:  # pragma: no cover — environment-specific
    QtWidgets = None  # type: ignore[assignment]
    HAS_QT = False


if HAS_QT:

    class BaseExtensionDialog(QtWidgets.QDialog):
        """Common scaffold for category-specific PyQt panels."""

        def __init__(self, title: str, parent: object | None = None) -> None:
            """Build an empty dialog with the given ``title``."""
            super().__init__(parent)
            self.setWindowTitle(title)
            self._build()

        def _build(self) -> None:
            """Hook for subclasses to assemble widgets. No-op by default."""

else:

    class BaseExtensionDialog:  # type: ignore[no-redef]
        """Stub used when PyQt5 is unavailable.

        Instantiation raises ``RuntimeError`` so callers notice the missing
        optional dependency.
        """

        def __init__(self, *args: object, **kwargs: object) -> None:
            """Raise ``RuntimeError`` — PyQt5 is not installed."""
            raise RuntimeError(
                "PyQt5 is not installed — install pymolish[gui] to use dialogs"
            )
