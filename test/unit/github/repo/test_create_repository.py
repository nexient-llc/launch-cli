from unittest.mock import MagicMock, patch

import pytest

from launch.github.repo import create_repository


@pytest.fixture
def repo_details():
    return {
        "organization": "test_org",
        "name": "test_repo",
        "description": "A test repository",
        "public": True,
        "visibility": "public",
    }


def test_create_repository_success(mocker, repo_details):
    mock_repo = MagicMock()
    mock_github = MagicMock()
    mock_github.get_organization.return_value.create_repo.return_value = mock_repo

    with patch("launch.github.repo.Github", return_value=mock_github):
        repo = create_repository(
            mock_github,
            repo_details["organization"],
            repo_details["name"],
            repo_details["description"],
            repo_details["public"],
            repo_details["visibility"],
        )

    mock_github.get_organization.assert_called_once_with(repo_details["organization"])
    mock_github.get_organization.return_value.create_repo.assert_called_once_with(
        name=repo_details["name"],
        description=repo_details["description"],
        private=not repo_details["public"],
        visibility=repo_details["visibility"],
        auto_init=True,
    )
    assert repo is mock_repo


def test_create_repository_exception(mocker, repo_details):
    mock_github = MagicMock()
    mock_github.get_organization.return_value.create_repo.side_effect = Exception(
        "Error"
    )

    with patch("launch.github.repo.Github", return_value=mock_github), pytest.raises(
        RuntimeError
    ) as exc_info:
        create_repository(
            mock_github,
            repo_details["organization"],
            repo_details["name"],
            repo_details["description"],
            repo_details["public"],
            repo_details["visibility"],
        )

    assert (
        str(exc_info.value)
        == f"Failed to create repository {repo_details['name']} in {repo_details['organization']}"
    )
