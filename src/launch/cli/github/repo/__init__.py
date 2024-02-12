import click

from .commands import create


@click.group(name="repo")
def repo_group():
    """Command family for dealing with GitHub repos."""


repo_group.add_command(create)
