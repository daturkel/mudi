from pathlib import Path
import frontmatter  # eyeseast/python-frontmatter
from typing import Optional, Tuple, Union

from .page import Page


def load_md_file(filename: Union[str, Path]) -> Tuple[str, dict]:
    result = frontmatter.load(filename)
    return result.content, result.metadata


def load_html_file(filename: Union[str, Path]) -> Tuple[str, dict]:
    with open(filename, "r") as f:
        content = f.read()
    return content, {}
