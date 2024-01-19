import click

from .commands import prepare


@click.group(name="terragrunt")
def terragrunt_group():
    """Command family for terragrunt-related tasks."""


terragrunt_group.add_command(prepare)
