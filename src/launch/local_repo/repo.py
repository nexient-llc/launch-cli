import logging
import subprocess

logger = logging.getLogger(__name__)


def checkout_branch(
    path: str, init_branch: str, main_branch: str, new_branch=False
) -> None:
    subprocess.run(["git", "pull", "origin", main_branch], cwd=path)
    if new_branch:
        subprocess.run(["git", "checkout", "-b", init_branch], cwd=path)
    else:
        subprocess.run(["git", "checkout", init_branch], cwd=path)


def push_branch(path: str, init_branch: str, commit_msg="Initial commit") -> None:
    subprocess.run(["git", "add", "."], cwd=path)
    subprocess.run(["git", "commit", "-m", commit_msg], cwd=path)
    subprocess.run(["git", "push", "--set-upstream", "origin", init_branch], cwd=path)
