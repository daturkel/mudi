from pydantic import BaseModel
from typing import Any, Optional


class CollectionSettings(BaseModel):
    name: str
    sort_key: Optional[str] = None
    sort_descending: bool = True
    sort_default: Any = None
