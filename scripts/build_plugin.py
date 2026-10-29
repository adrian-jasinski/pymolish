"""Build plugin/pymolish_<x>_<y>_<z>.zip with ``python scripts/build_plugin.py``.

Pass ``--unversioned`` to write plain ``plugin/pymolish.zip`` instead.
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


def main(versioned: bool = True) -> None:
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
                if relative == Path("pymolish/__init__.py"):
                    # PyMOL's Plugin Manager reads "# Key: value" comment lines
                    # at the top of __init__.py, so it can show the version
                    # without importing the package.
                    header = f"# Name: pymolish\n# Version: {version}\n"
                    archive.writestr(str(relative), header + path.read_text())
                else:
                    archive.write(path, relative)
        # ZIP installs have no package metadata; stamp the version in.
        archive.writestr("pymolish/_version.py", f'__version__ = "{version}"\n')

    print(f"Created {destination}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--unversioned",
        action="store_true",
        help="name the archive plain pymolish.zip",
    )
    main(not parser.parse_args().unversioned)
