import git
import pytest
from unittest.mock import patch, MagicMock
from launch.pipeline.common.functions import git_clone 


# Test for Successful Clone
def test_git_clone_success():
    with patch('git.Repo.clone_from') as mock_clone, \
         patch('launch.pipeline.common.functions.logger') as mock_logger:
        
        mock_clone.return_value = MagicMock(spec=git.Repo)
        target_dir = "target/directory"
        clone_url = "https://github.com/example/repo.git"

        repository = git_clone(False, target_dir, clone_url)

        mock_clone.assert_called_once_with(clone_url, target_dir)
        assert isinstance(repository, git.Repo)
        mock_logger.info.assert_any_call(f"Attempting to clone repository: {clone_url} into {target_dir}")
        mock_logger.info.assert_any_call(f"Repository {clone_url} cloned successfully to {target_dir}")

# Test where Git Clone Skipped
def test_git_clone_skipped():
    with patch('git.Repo.clone_from') as mock_clone, \
         patch('launch.pipeline.common.functions.logger') as mock_logger:
        
        target_dir = "target/directory"
        clone_url = "https://github.com/example/repo.git"

        repository = git_clone(True, target_dir, clone_url)

        mock_clone.assert_not_called()
        assert repository is None

# Test for Git Clone Failure
def test_git_clone_failure():
    with patch('git.Repo.clone_from', side_effect=git.GitCommandError("clone", "error")), \
         patch('launch.pipeline.common.functions.logger') as mock_logger:
        
        target_dir = "target/directory"
        clone_url = "https://github.com/example/repo.git"

        with pytest.raises(RuntimeError):
            git_clone(False, target_dir, clone_url)

        mock_logger.error.assert_called_once()
