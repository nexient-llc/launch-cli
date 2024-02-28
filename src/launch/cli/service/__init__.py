import click

from .commands import cleanup, create, generate, update


@click.group(name="service")
def service_group():
    """Command family for service-related tasks."""


service_group.add_command(create)
service_group.add_command(generate)
service_group.add_command(cleanup)
service_group.add_command(update)
