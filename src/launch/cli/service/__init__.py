import click

from .commands import create


@click.group(name="service")
def service_group():
    """Command family for service-related tasks."""


service_group.add_command(create)
