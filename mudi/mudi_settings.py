from pathlib import Path
import toml
from typing import Dict, Optional

from .models import CollectionSettings, FeedSettings, Feeds, SiteSettings


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

        self.collection_settings: Dict[str, CollectionSettings] = {}
        collection_settings_dict = settings_dict.pop("collections", {})
        for name, collection_settings in collection_settings_dict.items():
            self.collection_settings[name] = CollectionSettings(**collection_settings)
        self.feeds = Feeds(feeds=settings_dict.pop("feed", []))
        self.site_ctx = settings_dict.pop("ctx", {})
        self.site_settings = SiteSettings(**settings_dict)
