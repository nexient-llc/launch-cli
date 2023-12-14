import json
import click
import os
import subprocess


@click.command()
@click.option(
    "--dry-run",
    is_flag=True,
    default=False,
    help="Perform a dry run that reports on what it would do, but does not create webhooks.",
)
def plan(
    dry_run: bool,
):
    """terragrunt plan."""

    if dry_run:
        click.secho(
            "Performing a dry run, nothing will be updated", fg="yellow"
        )

    script_dir = os.path.dirname(os.path.realpath(__file__))
    shell_script_path = os.path.join(script_dir, '../scripts/common/scripts/spec_scripts/actions/codebuild/terragrunt-plan.sh')
    output = subprocess.call([shell_script_path])
    if output != 0:
        click.secho(
            "Failed to run terragrunt-plan.sh", fg="red"
        )
        raise click.Abort()
    else:
        click.secho(
            "terragrunt-plan.sh ran successfully", fg="green"
        )


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
    script_dir = os.path.dirname(os.path.realpath(__file__))
    shell_script_path = os.path.join(script_dir, '../scripts/common/scripts/spec_scripts/actions/codebuild/terragrunt-deploy.sh')
    output = subprocess.call([shell_script_path])
    if output != 0:
        click.secho(
            "Failed to run terragrunt-deploy.sh", fg="red"
        )
        raise click.Abort()
    else:
        click.secho(
            "terragrunt-deploy.sh ran successfully", fg="green"
        )