import re

import pytest
import requests
import responses

from launch.github import access


def test_access_grant_maintain(mocker):
    team = mocker.MagicMock()
    team.get_repo_permission = mocker.MagicMock(return_value=None)
    repo = mocker.MagicMock()

    access.grant_maintain(team, repo, dry_run=False)
    team.get_repo_permission.assert_called_once()
    team.set_repo_permission.assert_called_once()


def test_grant_maintain_dry_run(mocker):
    team = mocker.MagicMock()
    team.get_repo_permission = mocker.MagicMock(return_value=None)
    repo = mocker.MagicMock()

    access.grant_maintain(team, repo, dry_run=True)
    team.get_repo_permission.assert_called_once()
    team.set_repo_permission.assert_not_called()


def test_access_grant_admin(mocker):
    team = mocker.MagicMock()
    team.get_repo_permission = mocker.MagicMock(return_value=None)
    repo = mocker.MagicMock()

    access.grant_admin(team, repo, dry_run=False)
    team.get_repo_permission.assert_called_once()
    team.set_repo_permission.assert_called_once()


def test_grant_admin_dry_run(mocker):
    team = mocker.MagicMock()
    team.get_repo_permission = mocker.MagicMock(return_value=None)
    repo = mocker.MagicMock()

    access.grant_admin(team, repo, dry_run=True)
    team.get_repo_permission.assert_called_once()
    team.set_repo_permission.assert_not_called()


def test_configure_default_branch_protection_warns_on_default_branch_name(
    mocker, capsys
):
    mocked_default_branch = mocker.MagicMock()
    mocked_default_branch.name = "not-main"

    repo = mocker.MagicMock()
    repo.get_branch = mocker.MagicMock(return_value=mocked_default_branch)

    access.configure_default_branch_protection(repo=repo, dry_run=True)

    stdout, _ = capsys.readouterr()
    assert "WARNING" in stdout
    assert (
        f"uses default branch {mocked_default_branch.name}, should be main!" in stdout
    )


def test_configure_default_branch_protection(mocker):
    mocked_default_branch = mocker.MagicMock()
    mocked_default_branch.name = "main"

    repo = mocker.MagicMock()
    repo.get_branch = mocker.MagicMock(return_value=mocked_default_branch)

    with mocker.patch.context_manager(
        access, "set_require_approval_of_most_recent_reviewable_push"
    ):
        access.configure_default_branch_protection(repo=repo, dry_run=False)
        access.set_require_approval_of_most_recent_reviewable_push.assert_called_once()

    mocked_default_branch.edit_protection.assert_called_once()
    mocked_default_branch.edit_required_pull_request_reviews.assert_called_once()
    mocked_default_branch.edit_protection.assert_called_once()


def test_configure_default_branch_protection_dry_run(mocker):
    mocked_default_branch = mocker.MagicMock()
    mocked_default_branch.name = "main"

    repo = mocker.MagicMock()
    repo.get_branch = mocker.MagicMock(return_value=mocked_default_branch)

    with mocker.patch.context_manager(
        access, "set_require_approval_of_most_recent_reviewable_push"
    ):
        access.configure_default_branch_protection(repo=repo, dry_run=True)
        access.set_require_approval_of_most_recent_reviewable_push.assert_not_called()

    mocked_default_branch.edit_protection.assert_not_called()
    mocked_default_branch.edit_required_pull_request_reviews.assert_not_called()
    mocked_default_branch.edit_protection.assert_not_called()


@pytest.mark.parametrize(
    "bad_status_codes", [400, 401, 402, 403, 404, 405, 500, 501, 502, 503, 504]
)
def test_set_require_approval_of_most_recent_reviewable_push_not_ok_raises(
    mocker, bad_status_codes
):
    organization = mocker.MagicMock()
    repository = mocker.MagicMock()
    branch = mocker.MagicMock()

    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.PATCH,
            re.compile(".+"),
            body="",
            status=bad_status_codes,
            content_type="application/json",
        )
        with pytest.raises(RuntimeError):
            access.set_require_approval_of_most_recent_reviewable_push(
                organization=organization, repository=repository, branch=branch
            )


def test_set_require_approval_of_most_recent_reviewable_push_request_exception_raises(
    mocker,
):
    organization = mocker.MagicMock()
    repository = mocker.MagicMock()
    branch = mocker.MagicMock()

    mocker.patch.object(requests, "patch", side_effect=OSError)

    with pytest.raises(RuntimeError):
        access.set_require_approval_of_most_recent_reviewable_push(
            organization=organization, repository=repository, branch=branch
        )
