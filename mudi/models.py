from pathlib import Path
from pydantic import AnyHttpUrl, BaseModel, Field, ValidationError, validator
from typing import Any, Dict, List, Optional


class FeedSettings(BaseModel):
    collection: str
    filename: Path
    sort_on: str
    descending: bool = True


class Feeds(BaseModel):
    feeds: List[FeedSettings] = Field([])


class SassSettings(BaseModel):
    sass_in: Path = Path("sass")
    sass_out: Path = Path("css")
    output_style: str = "nested"

    @validator("output_style")
    def valid_output_style(cls, v):
        if v not in ["nested", "expanded", "compact", "compresed"]:
            raise ValueError(
                "must be one of 'nested', 'expanded', 'compact', 'compressed'"
            )
        return v


class SiteSettings(BaseModel):
    input_dir: Path = Path("input")
    output_dir: Path = Path("dist")
    template_dir: Path = Path("templates")
    content_dir: Path = Path("content")
    default_template: str = "default.html"
    absolute_link: Optional[AnyHttpUrl] = None
    sass: Optional[SassSettings] = None
