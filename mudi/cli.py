import click
from pathlib import Path
import shutil
from typing import Optional

from . import __version__
from .mudi_settings import MudiSettings
from .site import Site


# Reusable click.option decorators
def settings_file(function):
    function = click.option(
        "--settings_file",
        "-s",
        default="settings.toml",
        type=click.Path(),
        show_default=True,
        help="Path of mudi settings file.",
    )(function)
    return function


def output_dir(function):
    function = click.option("--output_dir", "-o", type=click.Path())(function)
    return function


# CLI definition
@click.group()
@click.pass_context
def cli(ctx):
    ctx.ensure_object(dict)


@cli.command()
def version():
    """Get the currently installed version of mudi."""
    print(__version__)


@cli.command()
@settings_file
@output_dir
@click.pass_context
def clean(ctx, settings_file: click.Path, output_dir: Optional[click.Path]):
    """Delete contents of the mudi output directory."""
    ctx.ensure_object(dict)
    ctx.obj["settings_file"] = Path(str(settings_file))
    ctx.obj["output_dir"] = Path(str(output_dir))

    site = Site.from_settings_file(
        ctx.obj["settings_file"], ctx.obj["output_dir"], fully_initialize=False
    )
    site.clean()


@cli.command()
@settings_file
@output_dir
@click.option("--clean", "-c", is_flag=True, help="Run `clean` before building.")
@click.pass_context
def build(
    ctx, settings_file: click.Path, output_dir: Optional[click.Path], clean: bool
):
    """Build website and save to the output directory."""
    ctx.ensure_object(dict)
    ctx.obj["settings_file"] = Path(str(settings_file))
    ctx.obj["output_dir"] = Path(str(output_dir))

    site = Site.from_settings_file(
        ctx.obj["settings_file"], ctx.obj["output_dir"], fully_initialize=False
    )
    if clean:
        site.clean()
    site.build()
