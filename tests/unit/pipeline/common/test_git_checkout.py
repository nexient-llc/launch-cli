import git
import pytest
from unittest.mock import patch, MagicMock
from launch.pipeline.common.functions import *

class MockRepo:
    def __init__(self):
        self.git = MagicMock()


def test_git_checkout_existing_branch():
    mock_repo = MockRepo()
    branch = "existing_branch"

    with patch('launch.pipeline.common.functions.logger') as mock_logger:
        git_checkout(mock_repo, branch)

    mock_repo.git.checkout.assert_called_once_with(branch)
    mock_logger.info.assert_called_once_with(f"Checked out branch: {branch}")


def test_git_checkout_new_branch():
    mock_repo = MockRepo()
    branch = "new_branch"

    with patch('launch.pipeline.common.functions.logger') as mock_logger:
        git_checkout(mock_repo, branch, new_branch=True)

    mock_repo.git.checkout.assert_called_once_with('-b', branch)
    mock_logger.info.assert_called_once_with(f"Checked out new branch: {branch}")


def test_git_checkout_existing_branch_git_command_error():
    mock_repo = MockRepo()
    mock_repo.git.checkout.side_effect = git.GitCommandError("checkout", "error")
    branch = "error_branch"

    with pytest.raises(RuntimeError, match=f"An error occurred while checking out {branch}"):
        git_checkout(mock_repo, branch)


def test_git_checkout_new_branch_git_command_error():
    mock_repo = MockRepo()
    mock_repo.git.checkout.side_effect = git.GitCommandError("checkout", "error")
    branch = "error_new_branch"

    with pytest.raises(RuntimeError, match=f"An error occurred while checking out {branch}"):
        git_checkout(mock_repo, branch, new_branch=True)
