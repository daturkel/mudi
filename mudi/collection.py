from __future__ import annotations

from typing import Any, List, Optional, Tuple

from .page import Page


class Collection:
    def __init__(self, name: str, pages: Optional[List[Page]] = None):
        self.name = name
        self.pages: List[Page] = pages or []

    def sorted_by(
        self, keys: List[Tuple[str, bool, Any]], name: Optional[str] = None
    ) -> Collection:
        if not len(self.pages):
            return Collection(name=name or self.name, pages=self.pages)
        sorted_pages = self.pages
        for key, reverse, default in reversed(keys):
            sorted_pages = sorted(
                sorted_pages, key=lambda x: x.get(key, default), reverse=reverse
            )
        return Collection(name=name or self.name, pages=sorted_pages)
