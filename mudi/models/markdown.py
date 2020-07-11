from pydantic import BaseModel, Field, validator
from typing import Any, Dict


class MarkdownSettings(BaseModel):
    output_format: str = "html5"
    tab_length: int = 2

    enable_checklist: bool = False

    enable_codehilite: bool = False
    codehilite_options: Dict[str, Any] = Field(
        {"css_class": "highlight", "guess_lang": False}
    )

    enable_fenced_code: bool = True

    enable_footnotes: bool = True
    footnotes_options: Dict[str, Any] = Field({"BACKLINK_TEXT": "&#x2191;"})

    enable_smartypants: bool = False
    smartypants_options: Dict[str, Any] = Field({})

    enable_toc: bool = False
    toc_options: Dict[str, Any] = Field({"anchorlink": True})

    enable_truly_sane_lists: bool = True
    truly_sane_lists_options: Dict[str, Any] = Field({"truly_sane": True})

    @validator("output_format")
    def valid_output_format(cls, v):
        if v in ["html5", "xhtml"]:
            return v
        else:
            raise ValueError("output_format must be html5 or xhtml")

    @validator("tab_length")
    def valid_tab_length(cls, v):
        if v > 0:
            return v
        else:
            raise ValueError("tab_length must be integer greater than 0")
