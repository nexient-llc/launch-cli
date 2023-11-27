import pytest
from git.repo import Repo
from semver import Version

from launch.local_repo import tags  # Used for mocking only
from launch.local_repo.tags import (
    acquire_repo,
    create_version_tag,
    push_version_tag,
    read_semantic_tags,
    read_tags,
)


def test_acquire_repo(example_github_repo):
    acquired_repo = acquire_repo(repo_path=example_github_repo.working_dir)
    assert example_github_repo == acquired_repo


def test_get_tags(example_github_repo):
    example_github_repo.create_tag("not-semantic!")
    tags = read_tags(repo_path=example_github_repo.working_dir)
    assert len(tags) == 2
    assert "0.1.0" in tags
    assert "not-semantic!" in tags


def test_get_semantic_tags(example_github_repo):
    example_github_repo.create_tag("not-semantic!")
    tags = read_semantic_tags(repo_path=example_github_repo.working_dir)
    assert len(tags) == 1
    assert Version.parse("0.1.0") in tags


def test_create_version_tag(example_github_repo):
    new_version = Version(major=1, minor=2, patch=3)
    new_ref = create_version_tag(
        repo_path=example_github_repo.working_dir, version=new_version
    )
    assert new_ref.name == "1.2.3"


def test_push_version_tag(example_github_repo, mocker):
    # Since we don't really have a remote to push to, mocking is about all we can do.
    new_version = Version(major=1, minor=0, patch=0)
    new_ref = create_version_tag(
        repo_path=example_github_repo.working_dir, version=new_version
    )
    repo_mock = mocker.MagicMock()
    mocker.patch.object(tags, "acquire_repo", return_value=repo_mock)
    push_version_tag(repo_path=example_github_repo.working_dir, tag=new_ref)
    repo_mock.remote.assert_called_with("origin")
    repo_mock.remote.call_count == 2
