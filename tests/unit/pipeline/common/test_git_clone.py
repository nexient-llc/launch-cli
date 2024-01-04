import pytest

from unittest.mock import patch, MagicMock
from launch.pipeline.common.functions import *


class MockRepo:
    @staticmethod
    def clone_from(clone_url, target_dir):
        return MockRepo()


def test_git_clone_success():
    with patch('git.Repo.clone_from') as mock_clone:
        mock_clone.return_value = MagicMock(spec=git.Repo)

        repository = git_clone("target/directory", "https://github.com/example/repo.git")
        
        mock_clone.assert_called_once_with("https://github.com/example/repo.git", "target/directory")
        assert isinstance(repository, git.Repo)


def test_git_clone_git_command_error():
    with patch('git.Repo.clone_from', side_effect=git.GitCommandError("clone", "error")):
        with pytest.raises(RuntimeError, match="An error occurred while cloning the repository"):
            git_clone("target/directory", "https://github.com/example/repo.git")
