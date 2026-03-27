"""
File and folder CRUD operations using pathlib.
All functions raise OSError (or subclasses) on failure.
"""

import shutil
from pathlib import Path


def create_file(parent_dir: Path, name: str) -> Path:
    """Create a new .gmi file in parent_dir. Appends .gmi if omitted."""
    if not name.endswith(".gmi"):
        name = name + ".gmi"
    path = parent_dir / name
    path.touch(exist_ok=False)  # raises FileExistsError if already present
    return path


def create_folder(parent_dir: Path, name: str) -> Path:
    """Create a new folder in parent_dir."""
    path = parent_dir / name
    path.mkdir(exist_ok=False)  # raises FileExistsError if already present
    return path


def rename(path: Path, new_name: str) -> Path:
    """Rename a file or folder. Returns the new path."""
    new_path = path.parent / new_name
    path.rename(new_path)
    return new_path


def delete(path: Path) -> None:
    """Delete a file or folder (recursive for directories)."""
    if path.is_dir():
        shutil.rmtree(path)
    else:
        path.unlink()
