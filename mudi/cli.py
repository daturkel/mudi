import click
from pathlib import Path
import shutil
from typing import Optional

from .mudi_environment import MudiEnvironment
from .utils import delete_directory_contents


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
def cli(ctx, config_file: click.Path, output_dir: Optional[click.Path]):
    ctx.ensure_object(dict)
    config_file_ = Path(str(config_file))
    output_dir_ = Path(str(output_dir))
    ctx.obj["mudi_environment"] = MudiEnvironment(config_file_, output_dir_)


@cli.command()
@click.pass_context
def clean(ctx):
    mudi_environment: MudiEnvironment = ctx["mudi_environment"]
    mudi_environment.clean()
