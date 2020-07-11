from pathlib import Path
from pydantic import BaseModel, validator


class SassSettings(BaseModel):
    sass_in: Path = Path("sass")
    sass_out: Path = Path("css")
    output_style: str = "nested"

    @validator("output_style")
    def valid_output_style(cls, v):
        if v not in ["nested", "expanded", "compact", "compressed"]:
            raise ValueError(
                "must be one of 'nested', 'expanded', 'compact', 'compressed'"
            )
        return v
