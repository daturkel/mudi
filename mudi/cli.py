import click
from pathlib import Path
import shutil
from typing import Optional

from .mudi_settings import MudiSettings
from .site import Site


@click.group()
@click.option(
    "--settings_file",
    "-s",
    default="settings.toml",
    type=click.Path(),
    show_default=True,
)
@click.pass_context
@click.option("--output_dir", "-o", type=click.Path())
def cli(ctx, settings_file: click.Path, output_dir: Optional[click.Path]):
    ctx.ensure_object(dict)
    ctx.obj["settings_file"] = Path(str(settings_file))
    ctx.obj["output_dir"] = Path(str(output_dir))


@cli.command()
@click.pass_context
def clean(ctx):
    site = Site.from_settings_file(
        ctx.obj["settings_file"], ctx["output_dir"], fully_initialize=False
    )
    site.clean()
