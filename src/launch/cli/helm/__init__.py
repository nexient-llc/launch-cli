import click

from .commands import resolve_dependencies


@click.group(name="helm")
def service_group():
    """Command family for helm-related tasks."""


service_group.add_command(resolve_dependencies)
