from unittest.mock import MagicMock, patch

import git
import pytest

from launch.automation.common.functions import git_clone


# Test for Successful Clone
def test_git_clone_success():
    with patch("launch.automation.common.functions.git.Repo.clone_from") as mock_clone:
        mock_clone.return_value = MagicMock(spec=git.Repo)
        target_dir = "target/directory"
        clone_url = "https://github.com/example/repo.git"

        repository = git_clone(False, target_dir, clone_url)

        mock_clone.assert_called_once_with(clone_url, target_dir)
        assert isinstance(repository, git.Repo)


# Test where Git Clone is Skipped and Repository is Successfully Retrieved
def test_git_clone_skipped_success():
    with patch("launch.automation.common.functions.Repo") as mock_repo:
        mock_repo.return_value = MagicMock(spec=git.Repo)
        target_dir = "target/directory"
        clone_url = "https://github.com/example/repo.git"

        repository = git_clone(True, target_dir, clone_url)

        assert isinstance(repository, git.Repo)


# Test for Git Clone Failure
def test_git_clone_failure():
    with patch(
        "launch.automation.common.functions.git.Repo.clone_from",
        side_effect=git.GitCommandError("clone", "error"),
    ):
        target_dir = "target/directory"
        clone_url = "https://github.com/example/repo.git"

        with pytest.raises(RuntimeError):
            git_clone(False, target_dir, clone_url)


# Test for Failure when Getting Repository in Skipped Mode
def test_git_clone_skipped_failure():
    with patch(
        "launch.automation.common.functions.git.Repo",
        side_effect=git.GitCommandError("get", "error"),
    ):
        target_dir = "target/directory"
        clone_url = "https://github.com/example/repo.git"

        with pytest.raises(RuntimeError):
            git_clone(True, target_dir, clone_url)
