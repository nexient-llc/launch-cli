import click

from .commands import apply, destroy, plan


@click.group(name="terragrunt")
def terragrunt_group():
    """Command family for terragrunt-related tasks."""


terragrunt_group.add_command(plan)
terragrunt_group.add_command(apply)
terragrunt_group.add_command(destroy)
