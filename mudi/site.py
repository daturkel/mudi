from collections import defaultdict
from jinja2 import Environment, FileSystemLoader, TemplateNotFound
from pathlib import Path
import sass
import shutil
import toml
from typing import DefaultDict, Dict, List, Optional, Union

from .collection import Collection
from .loaders import load_html_file, load_md_file
from .models import Feeds, SassSettings, SiteSettings
from .page import Page
from .utils import path_swap, rel_name


class Site:
    def __init__(
        self,
        site_settings: SiteSettings,
        ctx: Optional[dict] = None,
        feeds: Optional[Feeds] = None,
    ):

        self.settings = site_settings
        self.ctx = ctx if ctx is not None else {}
        self.feeds = feeds if feeds is not None else Feeds()

        self.files: List[Path] = []
        self.files_to_copy: List[Path] = []
        self.pages: Dict[str, Page] = {}
        self.collections: DefaultDict[str, List[Page]] = defaultdict(list)

        self.env = Environment(
            # cast template_dir to str to satisfy mypy on python versions <3.7
            # https://github.com/python/typeshed/blob/master/third_party/2and3/jinja2/loaders.pyi#L7-L12
            loader=FileSystemLoader(str(self.template_dir)),
            trim_blocks=True,
            lstrip_blocks=True,
        )
        self.env.globals = {
            "site": {"ctx": self.ctx, "settings": self.settings},
            "collections": self.collections,
            "feeds": self.feeds,
            "pages": self.pages,
        }

        self._parse_tree()

    @property
    def template_dir(self) -> Path:
        return self.settings.input_dir / self.settings.template_dir

    @property
    def content_dir(self) -> Path:
        return self.settings.input_dir / self.settings.content_dir

    @property
    def output_dir(self) -> Path:
        return self.settings.output_dir

    def is_sass_file(self, filename: Path) -> bool:
        if self.settings.sass is None:
            return False
        else:
            return (
                filename.suffix in [".sass", ".scss"]
                and self.settings.sass.sass_dir in filename.parents
            )

    def _parse_tree(self):
        self.files = [
            filename
            for filename in Path(self.content_dir).glob("**/*")
            if rel_name(filename, rel_path=self.content_dir)[0] != "."
        ]

        for filename in self.files:
            name = rel_name(filename, rel_path=self.content_dir)
            if Path(filename).suffix == ".md":
                content, metadata = load_md_file(filename)
                page = Page(name=name, content=content, metadata=metadata)
                self._register_page(page)
            elif Path(filename).suffix == ".html":
                # TODO: handle name collisions
                content, metadata = load_html_file(filename)
                page = Page(name=name, content=content, metadata=metadata)
                self._register_page(page)
            elif self.is_sass_file(Path(filename)):
                continue
            else:
                self.files_to_copy.append(filename)

        self.env.globals["pages"] = self.pages

    def _register_page(self, page: Page):
        self.pages[page.name] = page
        for collection in page.collections:
            self.collections[collection].append(page)
            self.env.globals["collections"] = self.collections

    def render_page(self, page: Page):
        template = self.env.get_template(
            page.template or self.settings.default_template
        )
        output = template.render(content=page.content, page=page)
        output_filename = self.settings.output_dir / Path(page.name).with_suffix(
            ".html"
        )
        output_filename.parent.mkdir(parents=True, exist_ok=True)
        with open(output_filename, "w") as f:
            f.write(output)

    def compile_sass(self):
        if self.sass_settings is not None:
            sass.compile(
                dirname=(self.sass_settings.sass_dir, self.sass_settings.css_dir),
                output_style=self.sass_settings.output_style,
            )

    def copy_file(self, filename: Path):
        output_filename = path_swap(filename, self.content_dir, self.output_dir)
        output_filename.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(filename, output_filename)

    def make(self):
        for file_ in self.files_to_copy:
            self.copy_file(file_)
        for page in self.pages.values():
            self._render_page(page)
        self._compile_sass()
