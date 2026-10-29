"""Exercise plugin startup and command isolation without optional packages."""

from __future__ import annotations

import subprocess
import sys
import textwrap
from pathlib import Path


def test_commands_remain_available_without_optional_dependencies():
    """Use a fresh interpreter so cached modules cannot hide eager imports."""
    script = textwrap.dedent(
        """
        import builtins
        import contextlib
        import io
        import sys
        from types import ModuleType
        from unittest.mock import MagicMock

        sys.path.insert(0, 'src')
        pymol = ModuleType('pymol')
        cmd = MagicMock()
        cmd.auto_arg = [{}, {}, {}, {}]
        pymol.cmd = cmd
        sys.modules['pymol'] = pymol

        original_import = builtins.__import__
        attempts = []
        optional = {'numpy', 'Bio', 'requests', 'matplotlib', 'PyQt5'}

        def import_without_extras(name, *args, **kwargs):
            if name.split('.')[0] in optional or name == 'pymol.Qt':
                attempts.append(name)
                raise ModuleNotFoundError(f'No module named {name!r}', name=name)
            return original_import(name, *args, **kwargs)

        builtins.__import__ = import_without_extras
        import pymolish
        from pymolish.core.registry import CommandRegistry

        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            pymolish.__init_plugin__()
        assert not attempts, attempts
        assert not output.getvalue(), output.getvalue()
        registry = CommandRegistry.instance()
        assert len(registry) == 49, len(registry)
        assert len(registry.categories()) == 6

        cases = [
            ('cluster_ligands_by_position', 'ligands', 'numpy', 'numpy', {}),
            ('cluster_ligands_from_group', 'ligands', 'numpy', 'numpy', {}),
            ('search_sequence', 'ACDEF', 'biopython', 'biopython', []),
        ]
        for name, argument, package, extra, empty in cases:
            cmd.reset_mock()
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                result = registry.get(name).function(argument)
            assert result == empty, (name, result)
            message = output.getvalue()
            assert f'{name} cannot run' in message, message
            assert f'{package} is required' in message, message
            assert f"pip install 'pymolish[{extra}]'" in message, message
            assert not cmd.mock_calls, cmd.mock_calls

        # An ordinary PyMOL command still works after dependency failures.
        cmd.reset_mock()
        cmd.count_atoms.side_effect = lambda selection: int('resn NA ' in selection)
        assert registry.get('remove_ions').function('all') == 1
        cmd.remove.assert_called_once_with('resn NA and (all)')

        # Gradient coloring also works with every optional library blocked.
        cmd.get_object_list.return_value = ['protein']
        cmd.get_color_tuple.return_value = (0.0, 0.0, 1.0)
        result = registry.get('color_group_with_gradient').function('all')
        assert result == {'protein': 'gradient_lightness_01'}, result
        cmd.color.assert_called_once()

        # Qt absence affects dialog construction, not GUI module imports.
        from pymolish.gui import HAS_QT, BaseExtensionDialog
        assert not HAS_QT
        try:
            BaseExtensionDialog('Test')
        except RuntimeError as error:
            assert 'pymolish[gui]' in str(error), error
        else:
            raise AssertionError('Dialog construction should require Qt')
        """
    )
    result = subprocess.run(
        [sys.executable, "-c", script],
        cwd=Path(__file__).resolve().parents[1],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, result.stdout + result.stderr
