from pathlib import Path
from pydantic import AnyHttpUrl, BaseModel, Field, ValidationError, validator
from typing import Any, Dict, List, Optional


class SassSettings(BaseModel):
    sass_dir: Path
    css_dir: Path
    output_style: str = "nested"

    @validator("output_style")
    def valid_output_style(cls, v):
        if v not in ["nested", "expanded", "compact", "compresed"]:
            raise ValueError(
                "must be one of 'nested', 'expanded', 'compact', 'compressed'"
            )
        return v


class FeedSettings(BaseModel):
    collection: str
    filename: Path
    sort_on: str
    descending: bool = True


class Feeds(BaseModel):
    feeds: List[FeedSettings] = Field([], alias="feed")


class SiteSettings(BaseModel):
    input_dir: Path = Path("input")
    output_dir: Path = Path("dist")
    template_dir: Path = Path("templates")
    content_dir: Path = Path("content")
    default_template: Path = Path("default.html")
    absolute_link: Optional[AnyHttpUrl] = None
