from markdown import Markdown
from markdown.extensions.codehilite import CodeHiliteExtension
from markdown.extensions.fenced_code import FencedCodeExtension
from markdown.extensions.footnotes import FootnoteExtension
from markdown.extensions.smarty import SmartyExtension
from markdown.extensions.toc import TocExtension
from markdown_checklist.extension import ChecklistExtension
from mdx_truly_sane_lists.mdx_truly_sane_lists import TrulySaneListExtension

from .models.markdown import MarkdownSettings


class MarkdownRenderer(Markdown):
    def __init__(self, settings: MarkdownSettings):
        self.settings = settings
        self.extensions = []

        if self.settings.enable_checklist:
            self.extensions.append(ChecklistExtension())

        if self.settings.enable_codehilite:
            self.extensions.append(
                CodeHiliteExtension(**self.settings.codehilite_options)
            )

        if self.settings.enable_fenced_code:
            self.extensions.append(FencedCodeExtension())

        if self.settings.enable_footnotes:
            self.extensions.append(FootnoteExtension(**self.settings.footnotes_options))

        if self.settings.enable_smartypants:
            self.extensions.append(SmartyExtension(**self.settings.smartypants_options))

        if self.settings.enable_toc:
            self.extensions.append(TocExtension(**self.settings.toc_options))

        if self.settings.enable_truly_sane_lists:
            self.extensions.append(
                TrulySaneListExtension(**self.settings.truly_sane_lists_options)
            )

        super().__init__(
            output_format=self.settings.output_format,
            tab_length=self.settings.tab_length,
            extensions=self.extensions,
        )
