import click
import json

from launch.github.hooks import (
    create_hook
)
from launch.github.auth import get_github_instance

@click.command()
@click.option(
    "--organization",
    default="nexient-llc",
    help="GitHub organization containing your repository. Defaults to the nexient-llc organization.",
)
@click.option(
    "--repository-name", 
    required=True, 
    help="Name of the repository to be updated."
)
@click.option(
    "--name",
    default="web",
    help="Use web to create a webhook. Default: web. This parameter only accepts the value web."
)
@click.option(
    "--config", 
    required=True, 
    help="Key/value pairs to provide settings for this webhook. E.x.: '{\"url\":\"<url>\",\"content_type\":\"json\",\"insecure_ssl\":\"0\"}'"
)
@click.option(
    "--events",
    default='["push"]',
    help="Determines what events the hook is triggered for. Default: '[\"push\"]'"
)
@click.option(
    "--active",
    default=True,
    help="Determines if notifications are sent when the webhook is triggered. Default is true."
)
@click.option(
    "--dry-run",
    is_flag=True,
    default=False,
    help="Perform a dry run that reports on what it would do, but does not create webhooks.",
)

def create(organization: str, repository_name: str, name: str, config: str, events: str, active: bool, dry_run: bool):
    """Creates a webhook for a single repository."""
    g = get_github_instance()


    repository = g.get_organization(login=organization).get_repo(name=repository_name)
    if dry_run:
        print("DRY RUN! NOTHING WILL BE UPDATED IN GITHUB!")
    create_hook(repo=repository, name=name, config=json.loads(config), events=json.loads(events),active=active,dry_run=dry_run)
