from pathlib import Path
from pydantic import BaseModel, Field
from typing import List


class FeedSettings(BaseModel):
    collection: str
    filename: Path
    sort_on: str
    descending: bool = True


class Feeds(BaseModel):
    feeds: List[FeedSettings] = Field([])
