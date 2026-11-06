# PyMOLish agent guide

PyMOL Open Source command extensions for Python 3.10+, with no required
third-party dependencies beyond the PyMOL host.

## Keep changes simple

Apply [Ponytail's rules](https://github.com/DietrichGebert/ponytail/blob/main/AGENTS.md)
within this project's architecture:

- Read the affected code, callers, tests, and relevant plans before editing. Use
  `rg` to find existing behavior and helpers.
- Prefer, in order: existing project code, stdlib or native PyMOL features, an
  existing optional dependency, then the smallest clear implementation.
- Complete the requested behavior and its affected callers, tests, and docs.
  Avoid speculative abstractions, wrappers, configuration, and unrelated cleanup.
- Keep helpers local until actual reuse warrants sharing. Fix a shared root cause
  once. Favor readable code over compressed one-liners.
- Preserve validation, error handling, security, and protection against losing
  files or PyMOL session data when simplifying.
- Test new nontrivial behavior and bug fixes with a focused regression test;
  trivial edits need no new tests.
- Comment non-obvious reasons. For a deliberate limitation, use
  `shortcut: <limit>, <when to revisit>` only when useful.
- Report what changed, checks run, and any relevant untested behavior or limits.

## Architecture and plans

Read the relevant sections of [ARCHITECTURE_PLAN.md](ARCHITECTURE_PLAN.md) and
related files in `plans/`. Preserve the registry, category, and optional GUI
boundaries. Implement only the part of the roadmap needed for the current task.

The architecture document includes historical examples and unchecked migration
steps. Verify them against current code and finalized plans; do not restore old
version literals, dependency names, or scaffolding just to match an example.
`pyproject.toml` defines the supported Python version, extras, and package version;
`LICENSE` defines the license.

| Location | Responsibility |
| --- | --- |
| `src/pymolish/__init__.py` | Plugin entry point, category discovery, meta-command registration, version lookup |
| `src/pymolish/core/` | Registry, completion, logging, CLI normalization, validators, group helpers, dependency installation and upgrades |
| `src/pymolish/extensions/<category>/` | Command implementations; each category's `__init_plugin__()` registers commands and completion |
| `src/pymolish/gui/` | Shared optional Qt infrastructure; category panels belong in `extensions/<category>/_gui.py` |
| `tests/` | pytest tests using the shared PyMOL mocks in `conftest.py` |
| `scripts/` | Command documentation generation and plugin ZIP build |
| `docs/commands/` | Generated command reference |

Current extension packages are `io`, `groups`, `structure`, `selection`, and
`visualization`; meta-commands use the `pymolish_` prefix. Animation and further
GUI panels are roadmap items, not requirements for unrelated changes.

Keep structured plans in `plans/active/` by default, or `plans/research/` for
requested research. Include a header, steps, expected outputs, and tags; refer
to plans by filename and move completed plans to `plans/finalized/`. Reusable
plan templates belong in `plans/templates/`. Small edits need no new plan file.

## Command conventions

- Register commands through `CommandRegistry.instance().register()` in the
  category initializer; only the registry calls `cmd.extend()`. Register
  completions there with `AutocompletionRegistry` and follow the existing
  bootstrap's completion setup.
- Include category, description, examples, tags, and `see_also` metadata. Keep
  typed return values and Google-style docstrings following Section 6 of the
  architecture plan, including PyMOL examples, `Since`, and `See Also`.
- Reuse `core/group_utils.py`, `core/validators.py` (including `coerce_bool`), and
  `core/cli.py` (`clean`) where appropriate; PyMOL command arguments can be strings.
- Module-level command imports may use stdlib, PyMOL, and lightweight project
  helpers. Import heavy optional packages inside the functions that need them.
  Missing extras must produce actionable install guidance without disabling
  unrelated commands or plugin startup.
- Use `plog()` for command diagnostics; keep imports silent and free of command
  registration side effects. Do not add module-level `print()` calls.
- Keep core commands usable without Qt. GUI features must use guarded
  `pymol.Qt` imports and handle its absence.

NumPy is needed for ligand clustering; Biopython for sequence search and an
optional UniProt fallback; RDKit for SMILES commands. UniProt fetching works
without Biopython, alignment statistics use `statistics`, and gradient colors
use stdlib. Matplotlib remains an available extra, not a gradient requirement.
Keep these dependencies optional; do not add required dependencies.

## Verification and delivery

Use the existing environment. Run relevant tests while iterating; for code
changes, finish with the repository checks:

```bash
.venv/bin/python -m pytest tests/
.venv/bin/ruff check .
.venv/bin/ruff format --check .
```

Format only files you change. Reuse `tests/conftest.py`; mock network calls and
PyMOL operations. Bootstrap or dependency changes should exercise
`tests/test_plugin_bootstrap.py` and `tests/test_optional_dependencies.py`.
Mocked tests do not establish that real PyMOL or Qt integration works.

- After changing command modules or the registry, update metadata/docstrings and
  run `.venv/bin/python scripts/generate_docs.py`; review the generated diff.
  Keep command additions, removals, and argument changes aligned with completion.
- After each task that changes code, bump the patch version in `pyproject.toml`
  only; `__version__` is derived from metadata or the ZIP's generated `_version.py`.
- After a version bump, add a newest-first entry to `CHANGELOG.md` with one bullet
  per user-visible change, then run `python3 scripts/build_plugin.py`.
  Documentation-only changes need no version bump or plugin rebuild.
- Preserve existing user changes. Do not commit unless explicitly asked.
- Do not modify `.venv/` or external libraries, write outside the repository, or
  remove `uv.lock` or `pyproject.toml` without user instruction.
