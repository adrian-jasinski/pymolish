"""Tests for the I/O extension sub-package bootstrap."""

from __future__ import annotations

import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

from pymolish.core.registry import CommandRegistry
from pymolish.extensions.io import __init_plugin__


def test_init_plugin_registers_all_io_commands(pymol_cmd):
    __init_plugin__(None)
    registry = CommandRegistry.instance()
    for name in (
        "load_files",
        "load_recursive",
        "list_loadable_files",
        "export_group",
        "export_objects",
        "export_by_pattern",
        "export_byres_to_csv",
    ):
        info = registry.get(name)
        assert info is not None, f"{name} should be registered"
        assert info.category == "I/O"
        assert info.examples  # every I/O command ships with examples


def test_init_plugin_registers_autocompletion(pymol_cmd):
    __init_plugin__(None)
    # After applying, auto_arg slot 0 should include load_files, export_group, etc.
    from pymolish.core.autocompletion import AutocompletionRegistry

    AutocompletionRegistry.instance().apply()
    commands_at_slot_0 = set(pymol_cmd.auto_arg[0].keys())
    assert {"load_files", "export_group", "export_byres_to_csv"} <= commands_at_slot_0


@pytest.mark.parametrize("missing_module", ["csv", "_csv"])
def test_plugin_loads_files_without_csv(missing_module):
    """Reproduce a Plugin Manager install with an incomplete Python runtime."""
    script = textwrap.dedent(
        """
        import builtins
        import contextlib
        import importlib
        import io
        import sys
        from pathlib import Path
        from tempfile import TemporaryDirectory
        from types import ModuleType
        from unittest.mock import MagicMock

        pymol = ModuleType('pymol')
        cmd = MagicMock()
        cmd.auto_arg = [{}, {}, {}, {}]
        cmd.get_names.return_value = []
        pymol.cmd = cmd
        sys.modules['pymol'] = pymol

        # Plugin Manager imports from pmg_tk.startup rather than sys.path.
        parent = ModuleType('pmg_tk')
        parent.__path__ = []
        startup = ModuleType('pmg_tk.startup')
        startup.__path__ = ['src']
        sys.modules[parent.__name__] = parent
        sys.modules[startup.__name__] = startup

        missing = sys.argv[1]
        for name in ('csv', '_csv'):
            sys.modules.pop(name, None)
        original_import = builtins.__import__

        def import_without_csv(name, *args, **kwargs):
            if name == missing:
                raise ModuleNotFoundError(f'No module named {name!r}', name=name)
            return original_import(name, *args, **kwargs)

        builtins.__import__ = import_without_csv
        plugin = importlib.import_module('pmg_tk.startup.pymolish')
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            plugin.__init_plugin__()
        assert not output.getvalue(), output.getvalue()
        registry = importlib.import_module(
            plugin.__name__ + '.core.registry'
        ).CommandRegistry.instance()
        assert len(registry.list_commands('I/O')) == 7

        with TemporaryDirectory() as directory:
            structure = Path(directory) / 'model.pdb'
            structure.write_text('END\\n')
            loaded = registry.get('load_files').function(directory, verbose=False)
            assert loaded == ['model'], loaded
            cmd.load.assert_called_once_with(str(structure), 'model')

            cmd.reset_mock()
            target = Path(directory) / 'residues.csv'
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                count = registry.get('export_byres_to_csv').function(
                    'all', str(target)
                )
            assert count == 0
            assert not target.exists()
            message = output.getvalue()
            assert 'export_byres_to_csv cannot run' in message, message
            assert missing in message, message
            assert 'standard library' in message, message
            assert not cmd.mock_calls, cmd.mock_calls
        """
    )
    result = subprocess.run(
        [sys.executable, "-c", script, missing_module],
        cwd=Path(__file__).resolve().parents[2],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, result.stdout + result.stderr
