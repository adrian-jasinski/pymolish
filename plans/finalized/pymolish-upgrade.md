# Plan: `pymolish_upgrade` — self-update from the GitHub `plugin/` folder

Tags: meta, upgrade, network, stdlib-only, reload

## Goal

One meta-command that checks GitHub for a newer `plugin/pymolish_<x>_<y>_<z>.zip`,
installs it over the running copy, and offers to reload the plugin in place
(yes / no dialog). A second meta-command does only the reload.

## Why in-process reload and not a process restart

PyMOL has no restart API. `os.execv` would work on Linux/macOS when PyMOL was
started from a Python script, but not for bundled builds (where
`sys.executable` is the PyMOL binary) and not on Windows, and it kills the
session. Purging `pymolish*` from `sys.modules` and re-running
`__init_plugin__` achieves the same (new code active, commands re-registered)
and keeps loaded objects. Trade-off: `importlib`-cached module objects held by
third parties stay stale; none exist today.

## Steps

1. `core/upgrade.py`
   - `_latest_release()` — `GET api.github.com/repos/adrian-jasinski/pymolish/contents/plugin`,
     regex `pymolish_(\d+)_(\d+)_(\d+)\.zip`, max tuple + `download_url`.
   - `_install(zip_path)` — extract with `zipfile`, replace the package dir the
     running module was imported from. Refuse when that dir is a symlink or not
     under `pymol.plugins.get_startup_path()` (protects dev checkouts and pip installs).
   - `pymolish_reload()` — purge `sys.modules`, `invalidate_caches`, re-import, `__init_plugin__`.
   - `pymolish_upgrade(check_only=0, restart=None)` — check → download → install →
     ask "Reload now?" via PyMOL's `tkMessageBox.askyesno` shim (Qt or Tk);
     no GUI → use `restart` arg; "no" → print how to reload / restart manually.
2. Register both in `_register_meta_commands`; autocomplete `check_only`.
3. `extensions/groups/_menu.py` — re-wrap on reload so the menu uses new code.
4. Tests: `tests/test_upgrade.py` with mocked `urlopen` and a tmp plugin dir.
5. Regenerate `docs/commands/meta.md`; bump version to 0.1.23.

## Expected output

```
PyMOL> pymolish_upgrade
[pymolish][upgrade] current 0.1.22, latest 0.1.23
[pymolish][upgrade] downloading pymolish_0_1_23.zip
[pymolish][upgrade] installed 0.1.23 into ~/.pymol/startup/pymolish
   (dialog) Reload pymolish now? [Yes] [No]
[pymolish][upgrade] reloaded: pymolish 0.1.23 (NN commands)
```
