from pathlib import Path
import shutil


def rel_name(filename: Path, rel_path: Path) -> Path:
    return filename.relative_to(rel_path).with_suffix("")


def path_swap(filename: Path, original_path: Path, new_path: Path) -> Path:
    base_name = rel_name(filename, original_path)
    return new_path / base_name


def delete_directory_contents(dir_path: Path):
    for child in dir_path.glob("*"):
        if child.is_file():
            child.unlink()
        else:
            shutil.rmtree(child)
