from jinja2 import Environment, FileSystemLoader, TemplateNotFound
import logging
from pathlib import Path
import sass
import shutil
import time
import toml
from typing import Dict, List, Optional, Union

from .collection import Collection
from .exceptions import NotInitializedError
from .loaders import load_html_file, load_md_file
from .markdown import MarkdownRenderer
from .models import (
    CollectionSettings,
    Feeds,
    MarkdownSettings,
    SassSettings,
    SiteSettings,
)
from .mudi_settings import MudiSettings
from .page import Page
from .utils import delete_directory_contents, rel_name, tictoc


class Site:
    def __init__(
        self,
        site_settings: SiteSettings,
        ctx: Optional[dict] = None,
        collection_settings: Optional[Dict[str, CollectionSettings]] = None,
        feeds: Optional[Feeds] = None,
        fully_initialize: bool = True,
    ):

        self.settings = site_settings
        self.collection_settings = (
            collection_settings if collection_settings is not None else {}
        )
        self.ctx = ctx if ctx is not None else {}
        self.feeds = feeds if feeds is not None else Feeds()

        self.files: List[Path] = []
        self.files_to_copy: List[Path] = []
        self.pages: Dict[str, Page] = {}
        self.collections: Dict[str, Collection] = dict()

        self.env: Environment

        self.fully_initialized = False
        if fully_initialize:
            self._fully_initialize()

    def __getattr__(self, key):
        try:
            return self.ctx[key]
        except KeyError as e:
            raise AttributeError(e)

    def _fully_initialize(self):
        if not self.fully_initialized:
            self._get_jinja_env()

            self._build_collections()
            self._parse_tree()

            self.md = MarkdownRenderer(self.settings.markdown)

            self.fully_initialized = True

    def _get_jinja_env(self):
        self.env = Environment(
            # cast template_dir to str to satisfy mypy on python versions <3.7
            # https://github.com/python/typeshed/blob/master/third_party/2and3/jinja2/loaders.pyi#L7-L12
            loader=FileSystemLoader(str(self.template_dir)),
            trim_blocks=True,
            lstrip_blocks=True,
        )
        self.env.globals = {
            "site": self,
            "collections": self.collections,
            "feeds": self.feeds,
            "pages": self.pages,
        }

    @classmethod
    def from_mudi_settings(
        cls, mudi_settings: MudiSettings, fully_initialize: bool = True,
    ):
        return cls(
            site_settings=mudi_settings.site_settings,
            ctx=mudi_settings.site_ctx,
            collection_settings=mudi_settings.collection_settings,
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
        logging.info(f"loaded settings from {settings_file}")
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

    def _build_collections(self):
        for collection_name, collection_settings in self.collection_settings.items():
            self.collections[collection_name] = Collection.from_collection_settings(
                collection_settings
            )

    def _parse_tree(self):
        self.files = [
            filename
            for filename in Path(self.content_dir).glob("**/*")
            if self._path_to_name(filename)[0] != "."
        ]

        for filename in self.files:
            if Path(filename).suffix == ".md":
                self.add_page_from_file(filename)
            elif Path(filename).suffix == ".html":
                # TODO: handle name collisions
                self.add_page_from_file(page)
            elif self.is_sass_file(Path(filename)):
                logging.debug(f"found sass file {filename}")
                continue
            elif Path(filename).is_file():
                logging.debug(f"{filename} → files to copy")
                self.files_to_copy.append(rel_name(filename, self.content_dir))

    def add_page(self, page: Page):
        self.pages[page.name] = page
        logging.info(self.collections)
        for collection in page.collections:
            if collection in self.collections:
                logging.info(f"adding {page.name} to collection")
                self.collections[collection].append(page)
            else:
                logging.info(f"building new collection")
                col = Collection(collection, [page])
                self.collections[collection] = col
            self.env.globals["collections"] = self.collections
        self.env.globals["pages"] = self.pages

    def add_page_from_file(self, filename: Path):
        name = self._path_to_name(filename)
        if filename.suffix == ".md":
            content, metadata = load_md_file(filename)
            page = Page(name=name, content=content, metadata=metadata,)
        elif filename.suffix == ".html":
            content, metadata = load_html_file(filename)
            page = Page(
                name=name, content=content, metadata=metadata, content_format="html"
            )
        logging.debug(f"{filename} → page '{page.name}'")
        self.add_page(page)

    def remove_page(self, page: Page):
        for collection in page.collections:
            self.collections[collection].remove(page)
        del self.pages[page.name]
        self.delete_file(Path(page.name + ".html"))
        self.env.globals["collections"] = self.collections
        self.env.globals["pages"] = self.pages

    def remove_page_from_file(self, filename: Path):
        name = self._path_to_name(filename)
        page = self.pages[name]
        self.remove_page(page)

    def render_page(self, page: Union[Page, str]):
        if isinstance(page, str):
            page = self.pages[page]

        if page.has_jinja:
            logging.debug(f"{page.name}: rendering inner jinja")
            content_template = self.env.from_string(page.content)
            content = content_template.render(page=page)
        else:
            content = page.content

        if page.content_format == "md":
            logging.debug(f"{page.name}: converting markdown")
            if page.markdown is not None:
                markdown_settings = self.settings.markdown.dict()
                markdown_settings.update(page.markdown)
                md = MarkdownRenderer(MarkdownSettings(**markdown_settings))
            else:
                md = self.md
            content = md.reset().convert(content).rstrip()

        logging.debug(f"{page.name}: rendering jinja")
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
        logging.info(f"wrote {page.name} to {output_filename}")

    def render_all_pages(self):
        logging.info("rendering...")
        for page in self.pages:
            self.render_page(page)
        logging.info("rendered html")

    def compile_sass(self):
        if self.settings.sass is not None:
            logging.info("compiling sass...")
            sass.compile(
                dirname=(self.sass_in, self.sass_out),
                output_style=self.settings.sass.output_style,
            )
            logging.info("compiled sass")

    def copy_file(self, filename: Path):
        input_filename = self.content_dir / filename
        output_filename = self.output_dir / filename
        output_filename.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(input_filename, output_filename)

    def copy_all_files(self):
        logging.info("copying files...")
        for file_ in self.files_to_copy:
            self.copy_file(file_)
        logging.info("copied files")

    def delete_file(self, filename: Path):
        logging.info(f"deleting file {filename}")
        output_filename = self.output_dir / filename
        output_filename.unlink()
        logging.info(f"deleted file")

    def build(self):
        tic = time.perf_counter()
        if self.fully_initialized:
            self.render_all_pages()
            self.compile_sass()
            self.copy_all_files()
            toc = time.perf_counter()
            logging.info(f"done in {tictoc(tic,toc)}s!")
        else:
            raise NotInitializedError(
                "Site must be fully initialized before building. Run _fully_initialize."
            )

    def clean(self):
        logging.info(f"Emptying {self.output_dir}")
        delete_directory_contents(self.output_dir)

    def _path_to_name(self, filename: Path) -> str:
        return str(rel_name(filename, rel_path=self.content_dir))
