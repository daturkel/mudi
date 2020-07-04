import click
from pathlib import Path
import shutil
from typing import Any, Callable, Dict, Optional

from . import __version__
from .logger import setup_logger
from .mudi_settings import MudiSettings
from .site import Site


def populate_context(
    settings_file: click.Path, output_dir: Optional[click.Path]
) -> dict:
    obj: Dict[str, Any] = {}
    obj["settings_file"] = Path(str(settings_file))
    if output_dir is not None:
        obj["output_dir"] = Path(str(output_dir))
    else:
        obj["output_dir"] = output_dir
    return obj


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


def output_dir(help_text: str = "Where mudi saves its output."):
    help_text += " [default: read from settings_file]"

    def output_dir_decorator(function: Callable):
        function = click.option(
            "--output_dir", "-o", type=click.Path(), help=help_text,
        )(function)
        return function

    return output_dir_decorator


# CLI definition
@click.group()
@click.pass_context
def cli(ctx):
    setup_logger()
    ctx.ensure_object(dict)


@cli.command()
def version():
    """Get the currently installed version of mudi."""
    click.echo(__version__)


@cli.command()
@settings_file
@output_dir("Output directory whose contents will be deleted.")
@click.pass_context
def clean(ctx, settings_file: click.Path, output_dir: Optional[click.Path]):
    """Delete contents of the mudi output directory."""
    ctx.ensure_object(dict)
    ctx.obj = populate_context(settings_file, output_dir)
    site = Site.from_settings_file(
        ctx.obj["settings_file"], ctx.obj["output_dir"], fully_initialize=False
    )
    site.clean()


@cli.command()
@settings_file
@output_dir()
@click.option("--clean", "-c", is_flag=True, help="Run `clean` before building.")
@click.pass_context
def build(
    ctx, settings_file: click.Path, output_dir: Optional[click.Path], clean: bool
):
    """Build website and save to the output directory."""
    ctx.ensure_object(dict)
    ctx.obj = populate_context(settings_file, output_dir)

    site = Site.from_settings_file(ctx.obj["settings_file"], ctx.obj["output_dir"])
    if clean:
        site.clean()
    site.build()
