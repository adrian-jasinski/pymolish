"""Build plugin/pymolish.zip with ``python scripts/build_plugin.py``.

Pass ``--versioned`` to name the archive after the package version instead,
e.g. ``plugin/pymolish_0_1_14.zip``.
"""

import argparse
import re
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

REPO_ROOT = Path(__file__).resolve().parent.parent


def package_version() -> str:
    """Read ``version`` from pyproject.toml (regex: tomllib needs 3.11)."""
    text = (REPO_ROOT / "pyproject.toml").read_text()
    return re.search(r'^version = "([^"]+)"', text, re.M).group(1)


def main(versioned: bool = False) -> None:
    """Archive the package for installation through PyMOL's Plugin Manager."""
    source = REPO_ROOT / "src" / "pymolish"
    version = package_version()
    name = "pymolish"
    if versioned:
        name += "_" + version.replace(".", "_")
    destination = REPO_ROOT / "plugin" / f"{name}.zip"
    destination.parent.mkdir(parents=True, exist_ok=True)

    with ZipFile(destination, "w", compression=ZIP_DEFLATED) as archive:
        for path in sorted(source.rglob("*")):
            relative = path.relative_to(source.parent)
            if (
                path.is_file()
                and "__pycache__" not in relative.parts
                and path.suffix not in {".pyc", ".pyo"}
            ):
                archive.write(path, relative)
        # ZIP installs have no package metadata; stamp the version in.
        archive.writestr("pymolish/_version.py", f'__version__ = "{version}"\n')

    print(f"Created {destination}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--versioned",
        action="store_true",
        help="name the archive pymolish_<major>_<minor>_<patch>.zip",
    )
    main(parser.parse_args().versioned)
