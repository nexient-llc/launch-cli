import os
import shutil
import pytest
import subprocess

from unittest.mock import patch, mock_open, MagicMock
from git.repo import Repo
from launch.pipeline.common.functions import *


@pytest.fixture(scope="function")
## GIT
def setup_git_repo():
    test_dir = "test_repo"
    clone_url = "https://github.com/example/repo.git"
    branch_name = "test"
    yield test_dir, clone_url, branch_name
    # Teardown: cleanup the cloned repository
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)

def test_clone(setup_git_repo):
    test_dir, clone_url, _ = setup_git_repo
    repo = git_clone(clone_url, test_dir)
    assert isinstance(repo, Repo)
    assert os.path.isdir(test_dir)
    assert os.path.isdir(os.path.join(test_dir, ".git"))

def test_checkout(setup_git_repo):
    test_dir, clone_url, branch_name = setup_git_repo
    repo = git_clone(clone_url, test_dir)
    git_checkout(repo, branch_name)
    assert repo.active_branch.name == branch_name

    new_branch_name = "new-test-branch"
    git_checkout(repo, new_branch_name, new_branch=True)
    assert repo.active_branch.name == new_branch_name

## Terragrunt
def test_run_terragrunt_init_success():
    with patch('subprocess.run') as mock_run:
        run_terragrunt_init()
        mock_run.assert_called_once_with(['terragrunt', 'init', '--terragrunt-non-interactive'], check=True)

def test_run_terragrunt_init_failure():
    with patch('subprocess.run', side_effect=subprocess.CalledProcessError(1, 'cmd')):
        with pytest.raises(RuntimeError):
            run_terragrunt_init()

def test_terragrunt_plan_success():
    with patch('subprocess.run') as mock_run:
        terragrunt_plan()
        mock_run.assert_called_once_with(['terragrunt', 'plan'], check=True)

def test_terragrunt_plan_with_file_success():
    with patch('subprocess.run') as mock_run:
        terragrunt_plan(file='test.tfplan')
        mock_run.assert_called_once_with(['terragrunt', 'plan', '-out', 'test.tfplan'], check=True)

def test_terragrunt_plan_failure():
    with patch('subprocess.run', side_effect=subprocess.CalledProcessError(1, 'cmd')):
        with pytest.raises(RuntimeError):
            terragrunt_plan()

def test_terragrunt_apply_success():
    with patch('subprocess.run') as mock_run:
        terragrunt_apply()
        mock_run.assert_called_once_with(['terragrunt', 'apply', '-auto-approve'], check=True)

def test_terragrunt_apply_with_file_success():
    with patch('subprocess.run') as mock_run:
        terragrunt_apply(file='variables.tfvars')
        mock_run.assert_called_once_with(['terragrunt', 'apply', '-var-file', 'variables.tfvars', '-auto-approve'], check=True)

def test_terragrunt_apply_failure():
    with patch('subprocess.run', side_effect=subprocess.CalledProcessError(1, 'cmd')):
        with pytest.raises(RuntimeError):
            terragrunt_apply()

def test_install_tool_versions_success():
    mock_file_content = "python 3.8.1\nnodejs 12.18.3"
    with patch('subprocess.run') as mock_run, \
         patch('open', mock_open(read_data=mock_file_content)), \
         patch('os.chdir') as mock_chdir:
        install_tool_versions()
        assert mock_run.call_count == 3  # Two plugins and one 'asdf install'
        mock_chdir.assert_called_once()

def test_install_tool_versions_exception():
    with patch('subprocess.run', side_effect=Exception('Test Error')), \
         patch('open', mock_open(read_data="")), \
         patch('os.chdir') as mock_chdir:
        with pytest.raises(RuntimeError):
            install_tool_versions()

def test_set_netrc_success():
    with patch('open', mock_open()) as mock_file, \
         patch('os.chmod') as mock_chmod:
        set_netrc('password123')
        mock_file.assert_called_once_with(os.path.expanduser('~/.netrc'), 'a')
        mock_chmod.assert_called_once_with(os.path.expanduser('~/.netrc'), 0o600)

def test_set_netrc_exception():
    with patch('open', side_effect=Exception('Test Error')), \
         patch('os.chmod'):
        with pytest.raises(RuntimeError):
            set_netrc('password123')
