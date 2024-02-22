import logging
import subprocess

from git import Repo

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
    except git.GitCommandError as e:
        raise RuntimeError(
            f"An error occurred while checking out {main_branch}:  {str(e)}"
        ) from e


def push_branch(path: str, branch: str, commit_msg="Initial commit") -> None:
    logger.info(f"path: {path}, branch: {branch}, commit_msg: {commit_msg}")
    subprocess.run(["git", "add", "."], cwd=path)
    subprocess.run(["git", "commit", "-m", commit_msg], cwd=path)
    subprocess.run(["git", "push", "--set-upstream", "origin", branch], cwd=path)
