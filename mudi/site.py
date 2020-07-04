from collections import defaultdict
from jinja2 import Environment, FileSystemLoader, TemplateNotFound
import logging
from pathlib import Path
import sass
import shutil
import toml
from typing import DefaultDict, Dict, List, Optional, Union

from .collection import Collection
from .exceptions import NotInitializedError
from .loaders import load_html_file, load_md_file
from .models import Feeds, SassSettings, SiteSettings
from .mudi_settings import MudiSettings
from .page import Page
from .utils import delete_directory_contents, path_swap, rel_name


class Site:
    def __init__(
        self,
        site_settings: SiteSettings,
        ctx: Optional[dict] = None,
        feeds: Optional[Feeds] = None,
        fully_initialize: bool = True,
    ):

        self.settings = site_settings
        self.ctx = ctx if ctx is not None else {}
        self.feeds = feeds if feeds is not None else Feeds()

        self.files: List[Path] = []
        self.files_to_copy: List[Path] = []
        self.pages: Dict[str, Page] = {}
        self.collections: DefaultDict[str, List[Page]] = defaultdict(list)

        self.env: Environment

        self.fully_initialized = False
        if fully_initialize:
            self._fully_initialize()

    def _fully_initialize(self):
        if not self.fully_initialized:
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

            self.fully_initialized = True

    @classmethod
    def from_mudi_settings(
        cls, mudi_settings: MudiSettings, fully_initialize: bool = True,
    ):
        return cls(
            site_settings=mudi_settings.site_settings,
            ctx=mudi_settings.site_ctx,
            feeds=mudi_settings.feeds,
            fully_initialize=fully_initialize,
        )

    @classmethod
    def from_settings_file(
        cls,
        settings_file: Path,
        output_dir: Optional[Path] = None,
        fully_initialize: bool = True,
    ):
        mudi_settings = MudiSettings(settings_file, output_dir)
        return cls.from_mudi_settings(mudi_settings, fully_initialize)

    @property
    def input_dir(self) -> Path:
        return self.settings.input_dir

    @property
    def template_dir(self) -> Path:
        return self.settings.input_dir / self.settings.template_dir

    @property
    def content_dir(self) -> Path:
        return self.settings.input_dir / self.settings.content_dir

    @property
    def output_dir(self) -> Path:
        return self.settings.output_dir

    @property
    def sass_in(self) -> Optional[Path]:
        if self.settings.sass is not None:
            return self.input_dir / self.settings.sass.sass_in
        else:
            return None

    @property
    def sass_out(self) -> Optional[Path]:
        if self.settings.sass is not None:
            return self.output_dir / self.settings.sass.sass_out
        else:
            return None

    def is_sass_file(self, filename: Path) -> bool:
        if self.settings.sass is None:
            return False
        else:
            return (
                filename.suffix in [".sass", ".scss"]
                and self.sass_in in filename.parents
            )

    def _parse_tree(self):
        self.files = [
            filename
            for filename in Path(self.content_dir).glob("**/*")
            if str(rel_name(filename, rel_path=self.content_dir))[0] != "."
        ]

        for filename in self.files:
            name = str(rel_name(filename, rel_path=self.content_dir))
            if Path(filename).suffix == ".md":
                content, metadata = load_md_file(filename)
                page = Page(name=name, content=content, metadata=metadata)
                logging.info(f"Registering {filename} as page {page.name}")
                self._register_page(page)
            elif Path(filename).suffix == ".html":
                # TODO: handle name collisions
                content, metadata = load_html_file(filename)
                page = Page(name=name, content=content, metadata=metadata)
                logging.info(f"Registering {filename} as page {page.name}")
                self._register_page(page)
            elif self.is_sass_file(Path(filename)):
                logging.info(f"Found sass file {filename}")
                continue
            else:
                logging.info(f"Will copy file {filename}")
                self.files_to_copy.append(filename)

        self.env.globals["pages"] = self.pages

    def _register_page(self, page: Page):
        self.pages[page.name] = page
        for collection in page.collections:
            self.collections[collection].append(page)
            self.env.globals["collections"] = self.collections

    def render_page(self, page: Union[Page, str]):
        if isinstance(page, str):
            page = self.pages[page]

        if page.has_jinja:
            content_template = self.env.from_string(page.content)
            content = content_template.render(page=page)
        else:
            content = page.content

        template = self.env.get_template(
            page.template or self.settings.default_template
        )
        output = template.render(content=content, page=page)
        output_filename = self.settings.output_dir / Path(page.name).with_suffix(
            ".html"
        )
        output_filename.parent.mkdir(parents=True, exist_ok=True)
        with open(output_filename, "w") as f:
            f.write(output)

    def render_all_pages(self):
        for page in self.pages:
            self.render_page(page)

    def compile_sass(self):
        if self.settings.sass is not None:
            sass.compile(
                dirname=(self.sass_in, self.sass_out),
                output_style=self.settings.sass.output_style,
            )

    def copy_file(self, filename: Path):
        output_filename = path_swap(filename, self.content_dir, self.output_dir)
        output_filename.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(filename, output_filename)

    def copy_all_files(self):
        for file_ in self.files_to_copy:
            self.copy_file(file_)

    def build(self):
        if self.fully_initialized:
            self.copy_all_files()
            self.render_all_pages()
            self.compile_sass()
        else:
            raise NotInitializedError(
                "Site must be fully initialized before building. Run _fully_initialize."
            )

    def clean(self):
        delete_directory_contents(self.output_dir)
