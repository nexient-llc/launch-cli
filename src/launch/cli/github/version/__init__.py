import click

from .commands import apply, predict


@click.group(name="version")
def version_group():
    """Command family for dealing with GitHub versioning."""


version_group.add_command(predict)
version_group.add_command(apply)
