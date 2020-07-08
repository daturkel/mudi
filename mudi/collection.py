from typing import Any, List, Optional, Tuple

from .page import Page


class Collection:
    def __init__(self, name: str, pages: Optional[List[Page]] = None):
        self.name = name
        self.pages: List[Page] = pages or []

    def __iter__(self):
        self._iter_index = -1
        return self

    def __next__(self):
        self._iter_index += 1
        if self._iter_index >= len(self.pages):
            raise StopIteration
        return self.pages[self._iter_index]

    def __contains__(self, key):
        if isinstance(key, str):
            return key in [page.name for page in self.pages]
        elif isinstance(key, Page):
            return key in self.pages
        else:
            raise TypeError("Key must be type str or Page")

    def append(self, page: Page):
        self.pages.append(page)

    def sorted_by(
        self,
        key: str,
        descending: bool = True,
        default: Any = None,
        name: Optional[str] = None,
    ) -> "Collection":
        new_name = self.name if name is None else name
        if not len(self.pages):
            return Collection(name=new_name, pages=self.pages)
        sorted_pages = sorted(
            self.pages, key=lambda x: x.get(key, default), reverse=descending
        )
        return Collection(name=new_name, pages=sorted_pages)
