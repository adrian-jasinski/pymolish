"""Install optional dependencies into the Python interpreter that runs PyMOL."""

from __future__ import annotations

import importlib
import importlib.util
import os
import shutil
import subprocess
import sys

from .logging import plog
from .validators import coerce_bool

_TAG = "deps"

# Mirrors [project.optional-dependencies] in pyproject.toml.
# extra -> (module to probe, pip requirement)
EXTRAS: dict[str, tuple[str, str]] = {
    "numpy": ("numpy", "numpy>=1.20"),
    "matplotlib": ("matplotlib", "matplotlib>=3.3"),
    "biopython": ("Bio", "biopython>=1.83"),
    "gui": ("pymol.Qt", "PyQt5>=5.15"),
}
# ponytail: "gui" stays out of "all" — a second Qt binding can break PyMOL's GUI.
_DEFAULT_EXTRAS = ("numpy", "matplotlib", "biopython")


def _is_installed(module: str) -> bool:
    try:
        return importlib.util.find_spec(module) is not None
    except (ImportError, ValueError):
        return False


def _pymol_python() -> str | None:
    """Return the interpreter running PyMOL, or ``None`` if it can't be found.

    Bundled PyMOL builds may set ``sys.executable`` to the PyMOL binary, so
    fall back to the python inside ``sys.prefix``.
    """
    if "python" in os.path.basename(sys.executable).lower():
        return sys.executable
    for rel in ("bin/python3", "bin/python", "python.exe"):
        candidate = os.path.join(sys.prefix, rel)
        if os.path.isfile(candidate):
            return candidate
    return None


def _installer(python: str) -> list[str] | None:
    """Return the install command prefix: pip if present, else uv."""
    if (
        subprocess.run(
            [python, "-m", "pip", "--version"], capture_output=True
        ).returncode
        == 0
    ):
        return [python, "-m", "pip", "install"]
    uv = shutil.which("uv")
    if uv:
        return [uv, "pip", "install", "--python", python]
    return None


def pymolish_install_deps(
    extras: str = "all",
    dry_run: bool | str | int = False,
) -> list[str]:
    """Install optional pymolish dependencies into PyMOL's own Python.

    Checks that the interpreter running PyMOL can ``import pymol`` (so the
    packages land where PyMOL will find them), skips packages that are
    already installed, then installs the rest with ``pip`` or, when pip is
    missing (e.g. uv-managed venvs), ``uv pip install --python <python>``.

    Args:
        extras: Comma- or space-separated extras: ``numpy``, ``matplotlib``,
            ``biopython``, ``gui``, or ``all`` (everything except ``gui``).
        dry_run: When truthy, only print the install command.

    Returns:
        Pip requirements that were (or, with *dry_run*, would be) installed.

    Examples:
        PyMOL> pymolish_install_deps
        PyMOL> pymolish_install_deps biopython
        PyMOL> pymolish_install_deps numpy matplotlib, dry_run=1

    Since:
        0.1.11

    See Also:
        pymolish_version
    """
    dry_run = coerce_bool(dry_run)
    names = [n for n in extras.replace(",", " ").lower().split() if n]
    if not names or "all" in names:
        names = list(_DEFAULT_EXTRAS)
    unknown = [n for n in names if n not in EXTRAS]
    if unknown:
        plog(
            _TAG,
            f"unknown extra(s): {', '.join(unknown)}; choose from "
            f"{', '.join(EXTRAS)}, all",
            "error",
        )
        return []

    python = _pymol_python()
    if python is None:
        plog(
            _TAG,
            f"cannot locate PyMOL's python (sys.executable={sys.executable})",
            "error",
        )
        return []
    check = subprocess.run([python, "-c", "import pymol"], capture_output=True)
    if check.returncode != 0:
        plog(
            _TAG,
            f"{python} cannot import pymol - refusing to install into the "
            "wrong environment",
            "error",
        )
        return []
    plog(_TAG, f"PyMOL python: {python}")

    missing = []
    for name in names:
        module, requirement = EXTRAS[name]
        if _is_installed(module):
            plog(_TAG, f"  {name}: already installed")
        else:
            missing.append(requirement)
    if not missing:
        plog(_TAG, "nothing to install")
        return []

    installer = _installer(python)
    if installer is None:
        plog(
            _TAG,
            "neither pip nor uv is available; install manually: "
            f"{python} -m pip install {' '.join(missing)}",
            "error",
        )
        return []
    command = installer + missing
    plog(_TAG, f"{'would run' if dry_run else 'running'}: {' '.join(command)}")
    if dry_run:
        return missing

    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        for line in (result.stderr or result.stdout).strip().splitlines()[-10:]:
            plog(_TAG, f"  {line}", "error")
        plog(_TAG, "install failed", "error")
        return []
    importlib.invalidate_caches()
    plog(_TAG, f"installed: {', '.join(missing)}")
    if "PyQt5>=5.15" in missing:
        plog(_TAG, "restart PyMOL to use the GUI panels")
    return missing
