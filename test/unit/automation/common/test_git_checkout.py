import pytest
from unittest.mock import MagicMock, patch
from launch.automation.common.functions import git_checkout
import git

# Test when skip_git is True
def test_git_checkout_skip_git():
    repository = MagicMock()
    git_checkout(True, repository)
    repository.git.checkout.assert_not_called()

# Test checking out an existing branch
@patch('launch.automation.common.functions.logger')
def test_git_checkout_existing_branch(mock_logger):
    repository = MagicMock()
    branch = 'existing_branch'
    git_checkout(False, repository, branch)
    repository.git.checkout.assert_called_once_with(branch)
    mock_logger.info.assert_called_once_with(f"Checked out branch: {branch}")

# Test creating and checking out a new branch
@patch('launch.automation.common.functions.logger')
def test_git_checkout_new_branch(mock_logger):
    repository = MagicMock()
    branch = 'new_branch'
    git_checkout(False, repository, branch, new_branch=True)
    repository.git.checkout.assert_called_once_with('-b', branch)
    mock_logger.info.assert_called_once_with(f"Checked out new branch: {branch}")

# Test GitCommandError exception handling
def test_git_checkout_git_command_error():
    repository = MagicMock()
    branch = 'faulty_branch'
    repository.git.checkout.side_effect = git.GitCommandError('checkout', 'error')
    
    with pytest.raises(RuntimeError):
        git_checkout(False, repository, branch)

