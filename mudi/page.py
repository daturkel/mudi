from pathlib import Path
from typing import Any, Optional, Tuple


class Page:
    def __init__(
        self, name: str, content: Optional[str] = None, metadata: Optional[dict] = None,
    ):
        """An object containing data needed to render a single page.

        Args:
            name (`str`): An identifier that is unique at the site level which also dictates
                the location of the output file (minus the extension).
            content (`str`, optional): A variable which is passed to the page's template
                under the name `content`. Defaults to `None`, which is converted to `""`.
            metadata (`dict`, optional): A set of variables associated with the page. Only
                certain reserved names will be saved, including `template`, dictating the
                Jinja template, and the `ctx` dictionary which can store arbitrary variables
                accessible to the template engine.

        Attributes:
            name (`str`): An identifier that is unique at the site level which also dictates
                the location of the output file (minus the extension).
            content (`str`): A variable which is passed to the page's template under the
                name `content`.
            template (`str`, optional): The name of the Jinja template used to render this
                page. Loaded from `metadata`. If `None`, the `Site`'s default template 
                will be used.
            collections (`List[str]`): A list of collections that this page belongs to.
            ctx (`Dict[str,Any]`): A namespace of variables accessible to the template
                engine as `page.ctx`.

        """
        self.name = name
        self.content = "" if content is None else content
        self.template: Optional[str]
        if metadata is None:
            self.template = None
            self.collections = []
            self.ctx = {}
        else:
            self.template = metadata.pop("template", None)
            self.collections = metadata.pop("collections", [])
            self.ctx = metadata.pop("ctx", {})

    def get(self, key: str, default: Any = None) -> Any:
        """Fetch a page attribute, first trying the page class attributes, then page ctx,
        and lastly resorting to a default.

        e.g. `page.get("foo", "bar")` checks for `page.foo`, then
        `page.ctx["foo"]`, and falls back to `"bar"`.

        Args:
            key (str): The name of the page attribute we want to get.
            default (Any, optional): The fallback if neither `self.key` nor `self.ctx[key]`
                are defined. Defaults to `None`.

        Returns:
            Any: `self.key` or `self.ctx[key]` or `default`, checked for existence in
                that order.

        """
        return getattr(self, key, self.ctx.get(key, default))