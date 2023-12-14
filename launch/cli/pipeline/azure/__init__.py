import click

from .terragrunt import terragrunt_group


@click.group(name="azure")
def azure_group():
    """Command family for Azure-related tasks."""


azure_group.add_command(terragrunt_group)
