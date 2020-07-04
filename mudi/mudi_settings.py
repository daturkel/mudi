from pathlib import Path
import toml
from typing import Optional

from .models import FeedSettings, Feeds, SiteSettings


class MudiSettings:
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
        self.site_ctx = settings_dict.pop("ctx", {})
        self.site_settings = SiteSettings(**settings_dict)
