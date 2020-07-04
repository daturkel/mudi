from pathlib import Path
import shutil
import toml
from typing import Optional

from .models import FeedSettings, Feeds, SassSettings, SiteSettings
from .site import Site
from .utils import delete_directory_contents


class MudiEnvironment:
    def __init__(
        self,
        settings_file: Path = Path("settings.toml"),
        output_dir: Optional[Path] = None,
    ):
        with open(settings_file, "r") as f:
            settings_dict = toml.load(f)

        # check for output_dir override
        if output_dir is not None:
            settings_dict["output_dir"] = output_dir

        self.feeds = Feeds(feeds=settings_dict.pop("feed", []))
        self._site_ctx = settings_dict.pop("ctx", {})
        self._site_settings = SiteSettings(**settings_dict)

        self._site: Optional[Site] = None

    def make_site_object(self):
        self._site = Site(
            site_settings=self.site_settings, ctx=self.site_ctx, feeds=self.feeds
        )

    @property
    def site(self) -> Site:
        if self._site is None:
            raise AttributeError(
                "MudiEnvironment has no site. Run make_site_object first."
            )
        return self._site

    @property
    def site_settings(self) -> SiteSettings:
        if self._site is None:
            return self._site_settings
        else:
            return self.site.settings

    @property
    def site_ctx(self) -> dict:
        if self._site is None:
            return self._site_ctx
        else:
            return self.site.ctx

    def clean(self):
        delete_directory_contents(self.site_settings.output_dir)
