import logging

import git
from git.repo import Repo
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


def clone_repository(repository_url: str, target: str, branch: str):
    try:
        logger.info(f"Attempting to clone repository: {repository_url} into {target}")
        repository = Repo.clone_from(repository_url, target, branch=branch)
        logger.info(f"Repository {repository_url} cloned successfully to {target}")
    except git.GitCommandError as e:
        logger.error(
            f"Error occurred while cloning the repository: {repository_url}, Error: {e}"
        )
        raise RuntimeError(
            f"An error occurred while cloning the repository: {repository_url}"
        ) from e
    return repository


def create_repository(
    g: Github,
    organization: str,
    name: str,
    description: str,
    public: bool,
    visibility: str,
) -> Repo:
    try:
        return g.get_organization(organization).create_repo(
            name=name,
            description=description,
            private=not public,
            visibility=visibility,
        )
    except Exception as e:
        raise RuntimeError(
            f"Failed to create repository {name} in {organization}"
        ) from e
