import json
import logging
import os
from pathlib import Path

import click

from launch.automation.terragrunt.functions import *

logger = logging.getLogger(__name__)


@click.command()
@click.option(
    "--repository-url",
    required=True,
    help="(Required) The URL of the service repository to run the terragrunt command against.",
)
@click.option(
    "--git-token",
    default=os.environ.get("GITHUB_TOKEN", None),
    required=True,
    help="(Required) The git token to use to clone the repositories. This defaults to the GIT_TOKEN environment variable.",
)
@click.option(
    "--commit-sha",
    help="The commit SHA or branch to checkout in the repository.",
)
@click.option(
    "--target-environment",
    default=os.environ.get("TARGETENV", "dev"),
    help="The target environment to run the terragrunt command against. Defaults to sandbox.",
)
@click.option(
    "--provider-config",
    default=None,
    help="Provider config is used for any specific config needed for certain providers. For example, AWS needs additional parameters to assume a deployment role. e.x {'provider':'aws','aws':{'role_arn':'arn:aws:iam::012345678912:role/myRole','region':'us-east-2'}}",
)
@click.option(
    "--skip-git",
    is_flag=True,
    default=False,
    help="If set, it will ignore cloning and checking out the git repository and it's properties.",
)
@click.option(
    "--skip-diff",
    is_flag=True,
    default=False,
    help="If set, it will ignore checking the diff between the pipeline and service changes.",
)
@click.option(
    "--is-infrastructure",
    is_flag=True,
    default=False,
    help="If set, this changes the path to the infrastructure directory for deployment to run terragrunt against.",
)
@click.option(
    "--path",
    default=Path.cwd(),
    help="Working directory path. Defaults to home (~).",
)
@click.option(
    "--override",
    type=dict,
    default={
        "infrastructure_dir": "platform/pipeline",
        "environment_dir": "platform/service",
        "properties_suffix": "properties",
        "main_branch": "main",
        "machine": "github.com",
        "login": "nobody",
        "tool_versions_file": ".tool-versions",
    },
    help="This is used to override the default values for various parameters. These are used for various use cases but you shouldn't have to change these. e.x {'infrastructure_dir':'platform/pipeline','environment_dir':'platform/service','properties_suffix':'properties','main_branch':'main','machine':'github.com','login':'nobody','tool_versions_file':'.tool-versions'}",
)
@click.option(
    "--dry-run",
    is_flag=True,
    default=False,
    help="Perform a dry run that reports on what it would do, but does not perform any action.",
)
def plan(
    repository_url: str,
    git_token: str,
    commit_sha: str,
    target_environment: str,
    provider_config: str,
    skip_git: bool,
    skip_diff: bool,
    is_infrastructure: bool,
    path: str,
    override: dict,
    dry_run: bool,
):
    """Runs terragrunt plan against a git repository and its properties repo."""

    if dry_run:
        click.secho("Performing a dry run, nothing will be updated", fg="yellow")

    prepare_for_terragrunt(
        repository_url=repository_url,
        git_token=git_token,
        commit_sha=commit_sha,
        target_environment=target_environment,
        provider_config=json.loads(provider_config),
        skip_git=skip_git,
        skip_diff=skip_diff,
        is_infrastructure=is_infrastructure,
        path=path,
        override=override,
    )

    terragrunt_init()
    terragrunt_plan()


@click.command()
@click.option(
    "--repository-url",
    required=True,
    help="(Required) The URL of the service repository to run the terragrunt command against.",
)
@click.option(
    "--git-token",
    default=os.environ.get("GITHUB_TOKEN", None),
    required=True,
    help="(Required) The git token to use to clone the repositories. This defaults to the GIT_TOKEN environment variable.",
)
@click.option(
    "--commit-sha",
    help="The commit SHA or branch to checkout in the repository.",
)
@click.option(
    "--target-environment",
    default=os.environ.get("TARGETENV", "dev"),
    help="The target environment to run the terragrunt command against. Defaults to sandbox.",
)
@click.option(
    "--provider-config",
    default=None,
    help="Provider config as a string used for any specific config needed for certain providers. For example, AWS needs additional parameters to assume a deployment role. e.x {'provider':'aws','aws':{'role_to_assume':'arn:aws:iam::012345678912:role/myRole','region':'us-east-2'}}",
)
@click.option(
    "--skip-git",
    is_flag=True,
    default=False,
    help="If set, it will ignore cloning and checking out the git repository and it's properties.",
)
@click.option(
    "--skip-diff",
    is_flag=True,
    default=False,
    help="If set, it will ignore checking the diff between the pipeline and service changes.",
)
@click.option(
    "--is-infrastructure",
    is_flag=True,
    default=False,
    help="If set, this changes the path to the infrastructure directory for deployment to run terragrunt against.",
)
@click.option(
    "--path",
    default=Path.cwd(),
    help="Working directory path. Defaults to home (~).",
)
@click.option(
    "--override",
    type=dict,
    default={
        "infrastructure_dir": "platform/pipeline",
        "environment_dir": "platform/service",
        "properties_suffix": "properties",
        "main_branch": "main",
        "machine": "github.com",
        "login": "nobody",
        "tool_versions_file": ".tool-versions",
    },
    help="This is used to override the default values for various parameters. These are used for various use cases but you shouldn't have to change these. e.x {'infrastructure_dir':'platform/pipeline','environment_dir':'platform/service','properties_suffix':'properties','main_branch':'main','machine':'github.com','login':'nobody','tool_versions_file':'.tool-versions'}",
)
@click.option(
    "--dry-run",
    is_flag=True,
    default=False,
    help="Perform a dry run that reports on what it would do, but does not perform any action.",
)
def apply(
    repository_url: str,
    git_token: str,
    commit_sha: str,
    target_environment: str,
    provider_config: dict,
    skip_git: bool,
    skip_diff: bool,
    is_infrastructure: bool,
    path: str,
    override: dict,
    dry_run: bool,
):
    """Runs terragrunt apply against a git repository and its properties repo."""

    if dry_run:
        click.secho("Performing a dry run, nothing will be updated", fg="yellow")

    prepare_for_terragrunt(
        repository_url=repository_url,
        git_token=git_token,
        commit_sha=commit_sha,
        target_environment=target_environment,
        provider_config=json.loads(provider_config),
        skip_git=skip_git,
        skip_diff=skip_diff,
        is_infrastructure=is_infrastructure,
        path=path,
        override=override,
    )

    terragrunt_init()
    terragrunt_apply()


@click.command()
@click.option(
    "--repository-url",
    required=True,
    help="(Required) The URL of the service repository to run the terragrunt command against.",
)
@click.option(
    "--git-token",
    default=os.environ.get("GITHUB_TOKEN", None),
    required=True,
    help="(Required) The git token to use to clone the repositories. This defaults to the GIT_TOKEN environment variable.",
)
@click.option(
    "--commit-sha",
    help="The commit SHA or branch to checkout in the repository.",
)
@click.option(
    "--target-environment",
    default=os.environ.get("TARGETENV", "dev"),
    help="The target environment to run the terragrunt command against. Defaults to sandbox.",
)
@click.option(
    "--provider-config",
    default=None,
    help="Provider config is used for any specific config needed for certain providers. For example, AWS needs additional parameters to assume a deployment role. e.x {'provider':'aws','aws':{'role_to_assume':'arn:aws:iam::012345678912:role/myRole','region':'us-east-2'}}",
)
@click.option(
    "--skip-git",
    is_flag=True,
    default=False,
    help="If set, it will ignore cloning and checking out the git repository and it's properties.",
)
@click.option(
    "--skip-diff",
    is_flag=True,
    default=False,
    help="If set, it will ignore checking the diff between the pipeline and service changes.",
)
@click.option(
    "--is-infrastructure",
    is_flag=True,
    default=False,
    help="If set, this changes the path to the infrastructure directory for deployment to run terragrunt against.",
)
@click.option(
    "--path",
    default=Path.cwd(),
    help="Working directory path. Defaults to home (~).",
)
@click.option(
    "--override",
    type=dict,
    default={
        "infrastructure_dir": "platform/pipeline",
        "environment_dir": "platform/service",
        "properties_suffix": "properties",
        "main_branch": "main",
        "machine": "github.com",
        "login": "nobody",
        "tool_versions_file": ".tool-versions",
    },
    help="This is used to override the default values for various parameters. These are used for various use cases but you shouldn't have to change these. e.x {'infrastructure_dir':'platform/pipeline','environment_dir':'platform/service','properties_suffix':'properties','main_branch':'main','machine':'github.com','login':'nobody','tool_versions_file':'.tool-versions'}",
)
@click.option(
    "--dry-run",
    is_flag=True,
    default=False,
    help="Perform a dry run that reports on what it would do, but does not perform any action.",
)
def destroy(
    repository_url: str,
    git_token: str,
    commit_sha: str,
    target_environment: str,
    provider_config: str,
    skip_git: bool,
    skip_diff: bool,
    is_infrastructure: bool,
    path: str,
    override: dict,
    dry_run: bool,
):
    """Runs terragrunt apply against a git repository and its properties repo."""

    if dry_run:
        click.secho("Performing a dry run, nothing will be updated", fg="yellow")

    prepare_for_terragrunt(
        repository_url=repository_url,
        git_token=git_token,
        commit_sha=commit_sha,
        target_environment=target_environment,
        provider_config=json.loads(provider_config),
        skip_git=skip_git,
        skip_diff=skip_diff,
        is_infrastructure=is_infrastructure,
        path=path,
        override=override,
    )

    terragrunt_init()
    terragrunt_destroy()
