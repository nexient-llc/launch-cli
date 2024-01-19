import click
import base64

from .commands import create
from launch.github.auth import get_github_instance
from launch.github.repo import create_repository

from launch import GITHUB_ORG_NAME, SERVICE_SKELETON

@click.command()
@click.option(
    "--repository-url",
    help="The URL of the repository to run this command against. If this not provided, it will attempted to run the command against the current directory.",
)
@click.option(
    "--name", 
    required=True, 
    help="Name of the service to  be created."
)
@click.option(
    "--dry-run",
    is_flag=True,
    default=False,
    help="Perform a dry run that reports on what it would do, but does not create webhooks.",
)
def prepare(
    repository_url: str,
    organization: str,
    name: str,
    description: str,
    skeleton: str,
    public: bool,
    visibility: str,
    dry_run: bool,
):
    """Creates a new service."""
    
    if dry_run:
        click.secho(
            "Performing a dry run, nothing will be created", fg="yellow"
        )
    
    g = get_github_instance()
    skeleton_repo = g.get_repo(skeleton)
    
    # clone dir
    # run make_configure
    # make dirs
    # run jinja2





