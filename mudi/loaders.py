import marko
from marko.ext.codehilite import CodeHilite
from pathlib import Path
import frontmatter  # eyeseast/python-frontmatter
from typing import Optional, Tuple, Union

from .page import Page

md = marko.Markdown(extensions=["footnote"])
md.use(CodeHilite(style="monokai"))


def load_md_file(filename: Union[str, Path]) -> Tuple[str, dict]:
    result = frontmatter.load(filename)
    content = marko.convert(result.content).rstrip()
    return content, result.metadata


def load_html_file(filename: Union[str, Path]) -> Tuple[str, dict]:
    with open(filename, "r") as f:
        content = f.read()
    return content, {}
