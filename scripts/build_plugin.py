"""Build plugin/pymolish.zip with ``python scripts/build_plugin.py``."""

from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

REPO_ROOT = Path(__file__).resolve().parent.parent


def main() -> None:
    """Archive the package for installation through PyMOL's Plugin Manager."""
    source = REPO_ROOT / "src" / "pymolish"
    destination = REPO_ROOT / "plugin" / "pymolish.zip"
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

    print(f"Created {destination}")


if __name__ == "__main__":
    main()
