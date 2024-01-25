import logging

from github import Github
from github.AuthenticatedUser import AuthenticatedUser
from github.Repository import Repository

logger = logging.getLogger(__name__)


def get_github_repos(
    g: Github, user: AuthenticatedUser | None = None
) -> list[Repository]:
    if user:
        return user.get_repos()
    repos = [repo for repo in g.get_user().get_repos()]
    logger.debug(f"Fetched {len(repos)}")
    return repos
