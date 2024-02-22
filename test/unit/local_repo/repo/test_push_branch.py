from unittest.mock import call, patch

import pytest

from launch.local_repo.repo import push_branch


@pytest.fixture
def git_details():
    return {
        "path": "/path/to/repo",
        "branch": "feature-branch",
        "default_commit_msg": "Initial commit",
        "custom_commit_msg": "Adds new feature",
    }


def test_push_branch_success(git_details):
    with patch("subprocess.run") as mock_run:
        push_branch(git_details["path"], git_details["branch"])
        calls = [
            call(["git", "add", "."], cwd=git_details["path"]),
            call(
                ["git", "commit", "-m", git_details["default_commit_msg"]],
                cwd=git_details["path"],
            ),
            call(
                ["git", "push", "--set-upstream", "origin", git_details["branch"]],
                cwd=git_details["path"],
            ),
        ]
        mock_run.assert_has_calls(calls)


def test_push_branch_custom_commit_message(git_details):
    with patch("subprocess.run") as mock_run:
        push_branch(
            git_details["path"], git_details["branch"], git_details["custom_commit_msg"]
        )
        mock_run.assert_any_call(
            ["git", "commit", "-m", git_details["custom_commit_msg"]],
            cwd=git_details["path"],
        )
