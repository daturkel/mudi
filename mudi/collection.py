from copy import deepcopy
from typing import Any, List, Optional, Tuple

from .page import Page


class Collection:
    def __init__(
        self,
        name: str,
        pages: Optional[List[Page]] = None,
        sort_key: Optional[str] = None,
        sort_descending: Optional[bool] = None,
        sort_default: Optional[Any] = None,
    ):
        self.name = name
        self._pages: List[Page] = pages or []
        self.sorted = sort_key is not None
        self.sort_key = sort_key
        self.sort_descending = sort_descending
        self.sort_default = sort_default

    @property
    def pages(self):
        # TODO: figure out a way to cache this intelligently
        if self.sorted:
            return self._sorted_by(
                self.sort_key, self.sort_descending, self.sort_default
            )
        else:
            return self._pages

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

    def _sorted_by(self, key: str, descending: bool = True, default: Any = None):
        if not len(self._pages):
            return self._pages
        sorted_pages = sorted(
            self.pages, key=lambda x: x.get(key, default), reverse=descending
        )
        return sorted_pages

    def sorted_by(
        self, key: str, descending: bool = True, default: Any = None,
    ) -> "Collection":
        if not len(self._pages):
            return self
        sorted_pages = self._sorted_by(key, descending, default)
        return Collection(name=self.name, pages=sorted_pages)

    def page(self, key: str) -> Page:
        if key not in self:
            raise KeyError(f"Collection has no page named {key}")
        else:
            page = list(filter(lambda p: p.name == key, self.pages))[0]
        this_index = self.pages.index(page)
        next_index = this_index + 1
        prev_index = this_index - 1
        if next_index < len(self.pages):
            next_ = self.pages[next_index]
        else:
            next_ = None
        if prev_index >= 0:
            prev = self.pages[prev_index]
        else:
            prev = None
        page.next = next_
        page.previous = prev
        return page
