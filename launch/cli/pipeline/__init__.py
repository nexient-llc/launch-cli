import click

from .aws import aws_group
from .azure import azure_group


@click.group(name="pipeline")
def pipeline_group():
    """Command family for Pipeline-related tasks."""


pipeline_group.add_command(aws_group)
pipeline_group.add_command(azure_group)
