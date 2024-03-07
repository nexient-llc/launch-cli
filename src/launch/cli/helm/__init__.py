import click

from .commands import resolve_dependencies


@click.group(name="helm")
def helm_group():
    """Command family for helm-related tasks."""


helm_group.add_command(resolve_dependencies)
