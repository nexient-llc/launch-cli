import json
import click
import subprocess

from launch.pipeline.common.functions import *


@click.command()
@click.option(
    "--repo-url",
)
@click.option(
    "--skip-git",
    is_flag=True,
    default=False,
    help="If set, it will ignore cloning and checking out a git repository. This assumes the command is already inside a git repository ready to be actioned.",
)
@click.option(
    "--dry-run",
    is_flag=True,
    default=False,
    help="Perform a dry run that reports on what it would do, but does not create webhooks.",
)
def plan(
    repository_url: str,
    skip_git: bool,
    dry_run: bool,
):
    """terragrunt plan."""

    if dry_run:
        click.secho(
            "Performing a dry run, nothing will be updated", fg="yellow"
        )

    if not skip_git:
        repository = git_clone(clone_url=repository_url)
        git_checkout(repository=repository)

    install_tool_versions()
    set_netrc(password=????)
    
    #TODO:
    #check for internals change

    

    prepare_for_terragrunt(
        repository=????,
        properties_suffix=????,
        target_environment=????,
        cloud_provider=os.environ['LAUNCH_PROVIDER']
    )

    #TODO:
    # Check if there are any changes to the internals folder
    # If there are, run the terragrunt plan for the internals folder
    # If there are not, run the terragrunt plan for the service folder
    # If the stage is not INTERNALS_PIPELINE, then run the terragrunt plan for the service folder
    

    terragrunt_init()
    terragrunt_plan()


@click.command()
@click.option(
    "--dry-run",
    is_flag=True,
    default=False,
    help="Perform a dry run that reports on what it would do, but does not create webhooks.",
)
def apply(
    dry_run: bool,
):
    """terragrunt apply."""

    if dry_run:
        click.secho(
            "Performing a dry run, nothing will be updated", fg="yellow"
        )
