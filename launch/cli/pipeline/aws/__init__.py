import click

from .terragrunt import terragrunt_group


@click.group(name="aws")
def aws_group():
    """Command family for AWS-related tasks."""


aws_group.add_command(terragrunt_group)
