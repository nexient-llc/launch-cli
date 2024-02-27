import logging
import subprocess

from git import GitCommandError, Repo

from launch import INIT_BRANCH

logger = logging.getLogger(__name__)


def checkout_branch(
    repository: Repo, main_branch: str, init_branch=INIT_BRANCH, new_branch=False
) -> None:
    try:
        if new_branch:
            repository.git.checkout("-b", init_branch)
            logger.info(f"Checked out new branch: {init_branch}")
        else:
            repository.git.checkout(main_branch)
            logger.info(f"Checked out branch: {main_branch}")
    except GitCommandError as e:
        raise RuntimeError(
            f"An error occurred while checking out {main_branch}:  {str(e)}"
        ) from e


def clone_repository(repository_url: str, target: str, branch: str) -> Repo:
    try:
        logger.info(f"Attempting to clone repository: {repository_url} into {target}")
        repository = Repo.clone_from(repository_url, target, branch=branch)
        logger.info(f"Repository {repository_url} cloned successfully to {target}")
    except GitCommandError as e:
        message = f"Error occurred while cloning the repository from {repository_url}"
        logger.exception(message)
        raise RuntimeError(message) from e
    return repository


def push_branch(path: str, branch: str, commit_msg="Initial commit") -> None:
    logger.info(f"path: {path}, branch: {branch}, commit_msg: {commit_msg}")
    subprocess.run(["git", "add", "."], cwd=path)
    subprocess.run(["git", "commit", "-m", commit_msg], cwd=path)
    subprocess.run(["git", "push", "--set-upstream", "origin", branch], cwd=path)
