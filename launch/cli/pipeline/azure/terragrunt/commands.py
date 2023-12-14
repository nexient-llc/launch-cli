import json
import click
import subprocess

from launch.pipeline.common.functions import *


@click.command()
@click.option(
    "--repo-url",
)
@click.option(
    "--skip-git",
    is_flag=True,
    default=False,
    help="If set, it will ignore cloning and checking out a git repository. This assumes the command is already inside a git repository ready to be actioned.",
)
@click.option(
    "--dry-run",
    is_flag=True,
    default=False,
    help="Perform a dry run that reports on what it would do, but does not create webhooks.",
)
def plan(
    repo_url: str,
    skip_git: bool,
    dry_run: bool,
):
    """terragrunt plan."""

    if dry_run:
        click.secho(
            "Performing a dry run, nothing will be updated", fg="yellow"
        )

    if not skip_git:
        repo = git_clone(clone_url=repo_url)
        git_checkout(repository=repo)

    # function terragrunt_plan {
    #     install_asdf "${HOME}"
    #     set_vars_script_and_clone_service
    #     git_checkout "${MERGE_COMMIT_ID}" "${CODEBUILD_SRC_DIR}/${GIT_REPO}"
    #     tool_versions_install "${CODEBUILD_SRC_DIR}/${GIT_REPO%"${PROPERTIES_REPO_SUFFIX}"}"
    #     set_netrc "${GIT_SERVER_URL}" "${GIT_USERNAME}" "${GIT_TOKEN}"
    #     cd "${CODEBUILD_SRC_DIR}/${GIT_REPO}" || exit 1

    #     if check_git_changes_for_internals "${MERGE_COMMIT_ID}" "${BUILD_BRANCH}" && [ "${INTERNALS_PIPELINE}" == "true" ]; then
    #         terragrunt_internals_loop "plan"
    #     elif ! check_git_changes_for_internals "${MERGE_COMMIT_ID}" "${BUILD_BRANCH}" && [ "${INTERNALS_PIPELINE}" == "true" ]; then
    #         echo "Exiting terragrunt plan as git changes found outside internals with this stage INTERNALS_PIPELINE == true"
    #         exit 0
    #     elif check_git_changes_for_internals "${MERGE_COMMIT_ID}" "${BUILD_BRANCH}" && [ "${INTERNALS_PIPELINE}" != "true" ]; then
    #         echo "Exiting terragrunt plan as git changes found inside internals with this stage INTERNALS_PIPELINE != true"
    #         exit 0
    #     else
    #         terragrunt_service_loop "plan"
    #     fi
    # }


@click.command()
@click.option(
    "--dry-run",
    is_flag=True,
    default=False,
    help="Perform a dry run that reports on what it would do, but does not create webhooks.",
)
def apply(
    dry_run: bool,
):
    """terragrunt apply."""

    if dry_run:
        click.secho(
            "Performing a dry run, nothing will be updated", fg="yellow"
        )
