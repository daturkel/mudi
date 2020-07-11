from pathlib import Path
from pydantic import AnyHttpUrl, BaseModel
from typing import Optional

from .markdown import MarkdownSettings
from .sass import SassSettings


class SiteSettings(BaseModel):
    input_dir: Path = Path("src")
    output_dir: Path = Path("dist")
    template_dir: Path = Path("templates")
    content_dir: Path = Path("content")
    default_template: str = "default.html"
    absolute_link: Optional[AnyHttpUrl] = None
    sass: Optional[SassSettings] = None
    markdown: MarkdownSettings = MarkdownSettings()
