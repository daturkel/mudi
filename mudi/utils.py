from pathlib import Path


def rel_name(filename: Path, rel_path: Path) -> Path:
    return filename.relative_to(rel_path).with_suffix("")


def path_swap(filename: Path, original_path: Path, new_path: Path) -> Path:
    base_name = rel_name(filename, rel_path)
    return new_path / base_name
