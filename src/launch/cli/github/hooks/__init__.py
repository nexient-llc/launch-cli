import click

from .commands import create


@click.group(name="hooks")
def hooks_group():
    """Command family for dealing with GitHub webhooks."""


hooks_group.add_command(create)
