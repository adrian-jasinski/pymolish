"""Self-update from the ``plugin/`` folder of the pymolish GitHub repository."""

from __future__ import annotations

import importlib
import json
import os
import re
import shutil
import sys
import tempfile
import urllib.request
import zipfile

from .logging import plog
from .validators import coerce_bool

_TAG = "upgrade"
_API = "https://api.github.com/repos/adrian-jasinski/pymolish/contents/plugin"
_ZIP_RE = re.compile(r"^pymolish_(\d+)_(\d+)_(\d+)\.zip$")
# "pmg_tk.startup.pymolish" when loaded by PyMOL's Plugin Manager, else "pymolish".
_PACKAGE = __name__.rsplit(".core.upgrade", 1)[0]
_PACKAGE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _version_tuple(version: str) -> tuple[int, ...]:
    return tuple(int(p) for p in re.findall(r"\d+", version)[:3])


def _latest_release() -> tuple[tuple[int, ...], str] | None:
    """Return ``(version, download_url)`` of the newest ZIP, or ``None``."""
    with urllib.request.urlopen(_API, timeout=30) as response:
        entries = json.load(response)
    found = [
        (tuple(int(g) for g in m.groups()), entry["download_url"])
        for entry in entries
        if (m := _ZIP_RE.match(entry.get("name", "")))
    ]
    return max(found) if found else None


def _download(url: str, directory: str) -> str:
    path = os.path.join(directory, "pymolish.zip")
    with urllib.request.urlopen(url, timeout=120) as response, open(path, "wb") as f:
        shutil.copyfileobj(response, f)
    return path


def _install_target() -> str | None:
    """The package dir to overwrite, or ``None`` when it is unsafe to do so."""
    try:
        from pymol.plugins import get_startup_path

        plugin_dirs = [os.path.abspath(p) for p in get_startup_path()]
    except Exception:  # noqa: BLE001 - no PyMOL, or mocked
        plugin_dirs = []
    if os.path.islink(_PACKAGE_DIR):
        plog(_TAG, f"{_PACKAGE_DIR} is a symlink (dev checkout) - not touched", "error")
        return None
    if os.path.dirname(_PACKAGE_DIR) not in plugin_dirs:
        plog(
            _TAG,
            f"pymolish runs from {_PACKAGE_DIR}, which is not a PyMOL plugin "
            "directory - upgrade it the way it was installed (pip/uv)",
            "error",
        )
        return None
    return _PACKAGE_DIR


def _install(zip_path: str, target: str) -> None:
    """Replace ``target`` with the ``pymolish/`` package inside ``zip_path``."""
    staging = tempfile.mkdtemp(prefix="pymolish-upgrade-")
    with zipfile.ZipFile(zip_path) as archive:
        if any(os.path.isabs(n) or ".." in n.split("/") for n in archive.namelist()):
            raise ValueError("archive contains unsafe paths")
        archive.extractall(staging)
    extracted = os.path.join(staging, "pymolish")
    if not os.path.isfile(os.path.join(extracted, "__init__.py")):
        raise ValueError("archive does not contain a pymolish package")
    shutil.rmtree(target)
    shutil.move(extracted, target)
    shutil.rmtree(staging, ignore_errors=True)


def _ask_yes_no(title: str, message: str) -> bool | None:
    """Ask through PyMOL's dialog shim (Qt or Tk); ``None`` when no GUI."""
    try:
        from pymol.plugins.legacysupport import tkMessageBox

        return bool(tkMessageBox.askyesno(title, message))
    except Exception:  # noqa: BLE001 - headless (pymol -c) or mocked
        return None


def pymolish_reload() -> str:
    """Reload pymolish in place and re-register every command.

    Drops all ``pymolish`` modules from ``sys.modules``, imports the package
    again from disk and runs its ``__init_plugin__``. Loaded objects and the
    PyMOL session are untouched. Use this after installing a new plugin ZIP
    without restarting PyMOL.

    Returns:
        The version string of the freshly loaded package.

    Examples:
        PyMOL> pymolish_reload

    Since:
        0.1.23

    See Also:
        pymolish_upgrade, pymolish_version
    """
    for name in list(sys.modules):
        parts = name.split(".")
        if "pymolish" in parts:
            del sys.modules[name]
    importlib.invalidate_caches()
    module = importlib.import_module(_PACKAGE)
    module.__init_plugin__(None)
    version = getattr(module, "__version__", "?")
    plog(_TAG, f"reloaded pymolish {version}")
    return version


def pymolish_upgrade(
    check_only: bool | str | int = False,
    restart: bool | str | int | None = None,
) -> str | None:
    """Upgrade pymolish from the newest ZIP in the GitHub ``plugin/`` folder.

    Lists ``plugin/pymolish_<x>_<y>_<z>.zip`` files on GitHub, and when one is
    newer than the running version downloads it and replaces the installed
    package (only when pymolish was installed through PyMOL's Plugin Manager;
    pip/uv installs and symlinked dev checkouts are refused). Afterwards a
    yes/no dialog offers to reload the plugin in place; declining leaves the
    old code running until you run ``pymolish_reload`` or restart PyMOL.

    Args:
        check_only: When truthy, only report whether a newer version exists.
        restart: Skip the dialog: ``1`` reloads right away, ``0`` never does.
            Also the fallback when no GUI dialog is available (``pymol -c``).

    Returns:
        The newer version string when one was found, ``None`` otherwise.

    Examples:
        PyMOL> pymolish_upgrade
        PyMOL> pymolish_upgrade check_only=1
        PyMOL> pymolish_upgrade restart=0

    Since:
        0.1.23

    See Also:
        pymolish_reload, pymolish_version
    """
    from .. import __version__

    check_only = coerce_bool(check_only)
    try:
        latest = _latest_release()
    except Exception as exc:  # noqa: BLE001 - network, rate limit, bad JSON
        plog(_TAG, f"cannot query GitHub: {exc}", "error")
        return None
    if latest is None:
        plog(_TAG, "no release ZIPs found on GitHub", "error")
        return None
    version_tuple, url = latest
    version = ".".join(map(str, version_tuple))
    plog(_TAG, f"current {__version__}, latest {version}")
    if version_tuple <= _version_tuple(__version__):
        plog(_TAG, "already up to date")
        return None
    if check_only:
        plog(_TAG, "run pymolish_upgrade to install it")
        return version

    target = _install_target()
    if target is None:
        return version
    plog(_TAG, f"downloading {os.path.basename(url)}")
    with tempfile.TemporaryDirectory() as tmp:
        try:
            _install(_download(url, tmp), target)
        except Exception as exc:  # noqa: BLE001
            plog(_TAG, f"install failed: {exc}", "error")
            return version
    plog(_TAG, f"installed {version} into {target}")

    do_reload = (
        coerce_bool(restart)
        if restart is not None
        else _ask_yes_no(
            "pymolish upgraded",
            f"pymolish {version} is installed.\nReload the plugin now?\n\n"
            "Loaded objects are kept; the old commands are replaced.",
        )
    )
    if do_reload:
        pymolish_reload()
    else:
        plog(_TAG, "not reloaded - run pymolish_reload or restart PyMOL to use it")
    return version
