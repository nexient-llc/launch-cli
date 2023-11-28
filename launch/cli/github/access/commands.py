import logging

import click

from launch.github.access import (
    configure_default_branch_protection,
    grant_admin,
    grant_maintain,
)
from launch.github.auth import get_github_instance

logger = logging.getLogger(__name__)


@click.command()
@click.option(
    "--organization",
    default="nexient-llc",
    help="GitHub organization containing your repository. Defaults to the nexient-llc organization.",
)
@click.option(
    "--repository-name", required=True, help="Name of the repository to be updated."
)
@click.option(
    "--dry-run",
    is_flag=True,
    default=False,
    help="Perform a dry run that reports on what it would do, but does not update access.",
)
def set_default(organization: str, repository_name: str, dry_run: bool):
    """Sets the default access and branch protections for a single repository."""
    g = get_github_instance()
    platform_team = g.get_organization(login=organization).get_team_by_slug("platform")
    platform_admin_team = g.get_organization(login=organization).get_team_by_slug(
        "platform-administrators"
    )
    repository = g.get_organization(login=organization).get_repo(name=repository_name)
    if dry_run:
        click.secho(
            "Performing a dry run, nothing will be updated in GitHub", fg="yellow"
        )
    grant_maintain(team=platform_team, repo=repository, dry_run=dry_run)
    grant_admin(team=platform_admin_team, repo=repository, dry_run=dry_run)
    configure_default_branch_protection(repo=repository, dry_run=dry_run)
