import requests
from github.Branch import Branch
from github.Organization import Organization
from github.Permissions import Permissions
from github.Repository import Repository
from github.Team import Team

from .auth import github_headers


def grant_maintain(team: Team, repo: Repository, dry_run=True) -> None:
    expected_permissions = {
        "triage": True,
        "push": True,
        "pull": True,
        "maintain": True,
        "admin": False,
    }

    existing_permissions: Permissions = team.get_repo_permission(repo=repo)

    needs_update = False

    if existing_permissions is not None:
        for permission, value in expected_permissions.items():
            if not getattr(existing_permissions, permission) == value:
                needs_update = True
    else:
        needs_update = True

    if needs_update:
        print(f"Granting maintain permissions to {team.slug} on {repo.url}")
        if not dry_run:
            team.set_repo_permission(repo=repo, permission="maintain")
    else:
        print(f"Permissions are already in place for {team.slug} on {repo.url}")


def grant_admin(team: Team, repo: Repository, dry_run=True) -> None:
    expected_permissions = {
        "triage": True,
        "push": True,
        "pull": True,
        "maintain": True,
        "admin": True,
    }

    existing_permissions: Permissions = team.get_repo_permission(repo=repo)

    needs_update = False

    if existing_permissions is not None:
        for permission, value in expected_permissions.items():
            if not getattr(existing_permissions, permission) == value:
                needs_update = True
    else:
        needs_update = True

    if needs_update:
        print(f"Granting admin permissions to {team.slug} on {repo.url}")
        if not dry_run:
            team.set_repo_permission(repo=repo, permission="admin")
    else:
        print(f"Permissions are already in place for {team.slug} on {repo.url}")


def configure_default_branch_protection(repo: Repository, dry_run=True) -> None:
    default_branch: Branch = repo.get_branch(repo.default_branch)
    if not default_branch.name == "main":
        print(
            f"WARNING: Repository at {repo.url} uses default branch {default_branch.name}, should be main!"
        )

    default_protections = {
        "enforce_admins": False,
        "dismiss_stale_reviews": False,
        "require_code_owner_reviews": True,
        "required_approving_review_count": 2,
        "required_linear_history": True,
        "allow_force_pushes": False,
        "block_creations": True,
        "required_conversation_resolution": False,
        "lock_branch": False,
        "allow_fork_syncing": True,
    }

    if not dry_run:
        print(
            f"Applying default branch protection to {default_branch.name} for repo {repo.url}"
        )
        default_branch.edit_protection(**default_protections)
        default_branch.edit_required_pull_request_reviews(
            require_code_owner_reviews=True, required_approving_review_count=2
        )
        set_require_approval_of_most_recent_reviewable_push(
            organization=repo.organization,
            repository=repo,
            branch=default_branch,
        )
    else:
        print(
            f"Would have applied default branch protection to {default_branch.name} for repo {repo.url}"
        )


def set_require_approval_of_most_recent_reviewable_push(
    organization: Organization, repository: Repository, branch: Branch
) -> None:
    """Hack to work around the fact that PyGithub doesn't support setting this configuration natively.

    Args:
        organization (Organization): GitHub Organization
        repository (Repository): GitHub Repository
        branch_name (Branch): Repository Branch

    Raises:
        RuntimeError: Raised if there was an issue setting this configuration
    """
    url = f"https://api.github.com/repos/{organization.login}/{repository.name}/branches/{branch.name}/protection/required_pull_request_reviews"
    payload = {"require_last_push_approval": True}
    try:
        response = requests.patch(url=url, json=payload, headers=github_headers())
        if not response.ok:
            raise RuntimeError(
                f"Failed to set_require_approval_of_most_recent_reviewable_push to {url}: Status Code: {response.status_code} Body: {response.text}"
            )
    except RuntimeError as re:
        raise re
    except Exception as e:
        raise RuntimeError(
            f"Failed to set_require_approval_of_most_recent_reviewable_push to {url}"
        ) from e
