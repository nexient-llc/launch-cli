import click

from .commands import set_default


@click.group(name="access")
def access_group():
    """Command family for dealing with GitHub access."""


access_group.add_command(set_default)
