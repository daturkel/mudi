import logging
from pathlib import Path
import watchgod

from .site import Site
from .utils import rel_name
from .watcher import MudiWatcher


class MudiDispatcher:
    def __init__(self, site: Site):
        self.site = site

    def _dispatch(self, change_type: watchgod.Change, path: Path):
        if self.site.template_dir in path.parents:
            self._dispatch_template(change_type, path)
        elif self.site.sass_in in path.parents:
            self._dispatch_sass(change_type, path)
        elif self.site.content_dir in path.parents:
            if path.suffix in [".html", ".md"]:
                self._dispatch_page(change_type, path)
            else:
                self._dispatch_file(change_type, path)
        logging.info("ready...")

    def _dispatch_template(self, change_type: watchgod.Change, path: Path):
        logging.info("reinitializing jinja")
        self.site._get_jinja_env()
        self.site.render_all_pages()

    def _dispatch_sass(self, change_type: watchgod.Change, path: Path):
        self.site.compile_sass()

    def _dispatch_page(self, change_type: watchgod.Change, path: Path):
        if change_type.name == "added":
            self.site.add_page_from_file(path)
            self.site.render_all_pages()
        elif change_type.name == "modified":
            self.site.remove_page_from_file(path)
            self.site.add_page_from_file(path)
            self.site.render_all_pages()
        elif change_type.name == "deleted":
            self.site.remove_page_from_file(path)
            self.site.render_all_pages()

    def _dispatch_file(self, change_type: watchgod.Change, path: Path):
        path = rel_name(path, self.site.content_dir)
        if change_type.name in ["added", "modified"]:
            self.site.copy_file(path)
        else:
            self.site.delete_file(path)

    def watch(self):
        for changes in watchgod.watch(
            ".", watcher_cls=MudiWatcher, watcher_kwargs={"site": self.site}
        ):
            for change_type, path in changes:
                logging.info(f"{path} {change_type.name}")
                path = Path(path)
                self._dispatch(change_type, path)
