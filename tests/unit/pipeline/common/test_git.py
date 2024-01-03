import os
import shutil
import pytest

from git.repo import Repo
from launch.pipeline.common.functions import *


@pytest.fixture(scope="function")

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