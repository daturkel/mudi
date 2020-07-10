from enum import IntEnum
import logging
from os import DirEntry
from pathlib import Path
from typing import Optional, Union
from watchgod import DefaultDirWatcher

from .site import Site


class MudiWatcher(DefaultDirWatcher):
    def __init__(self, root_path: Union[Path, str], site: Site):
        self.site = site
        self.output_dir = self.site.output_dir
        self.input_dir = self.site.input_dir
        self.content_dir = self.site.content_dir
        self.template_dir = self.site.template_dir
        self.sass_dir: Optional[Path]
        if self.site.settings.sass:
            self.sass_dir = self.site.sass_in
        else:
            self.sass_dir = None

        super().__init__(self.input_dir)
