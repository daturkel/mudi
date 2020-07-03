from typing import List, Optional

from .page import Page


class Collection:
    def __init__(self, name: str, pages: Optional[List[Page]] = None):
        self.name = name
        self.pages = [] if pages is not None else pages

    def sorted_by(keys: List[Tuple[str, str, str]]) -> List[str]:
        if not len(self.pages):
            return self.pages
        sorted_pages = self.pages
        for key, reverse, default in reversed(keys):
            sorted_pages = sorted(
                pages, key=lambda x: x.get(key, default), reverse=reverse
            )
        return [page.name for page in sorted_pages]
