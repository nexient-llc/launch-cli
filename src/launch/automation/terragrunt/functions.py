import logging
import os
import subprocess

from git import Repo

from launch import CODE_GENERATION_DIR_SUFFIX
from launch.automation.common.functions import (
    check_git_changes,
    deploy_remote_state,
    install_tool_versions,
    make_configure,
    set_netrc,
)
from launch.automation.provider.aws.functions import assume_role

logger = logging.getLogger(__name__)


## Terragrunt Specific Functions
def terragrunt_init(run_all=True):
    logger.info("Running terragrunt init")
    if run_all:
        subprocess_args = [
            "terragrunt",
            "run-all",
            "init",
            "--terragrunt-non-interactive",
        ]
    else:
        subprocess_args = ["terragrunt", "init", "--terragrunt-non-interactive"]

    try:
        subprocess.run(subprocess_args, check=True)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"An error occurred: {str(e)}")


def terragrunt_plan(file=None, run_all=True):
    logger.info("Running terragrunt plan")
    if run_all:
        subprocess_args = ["terragrunt", "run-all", "plan"]
    else:
        subprocess_args = ["terragrunt", "plan"]

    if file:
        subprocess_args.append("-out")
        subprocess_args.append(file)
    try:
        subprocess.run(subprocess_args, check=True)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"An error occurred: {str(e)}")


def terragrunt_apply(file=None, run_all=True):
    logger.info("Running terragrunt apply")
    if run_all:
        subprocess_args = [
            "terragrunt",
            "run-all",
            "apply",
            "-auto-approve",
            "--terragrunt-non-interactive",
        ]
    else:
        subprocess_args = [
            "terragrunt",
            "apply",
            "-auto-approve",
            "--terragrunt-non-interactive",
        ]

    if file:
        subprocess_args.append("-var-file")
        subprocess_args.append(file)
    try:
        subprocess.run(subprocess_args, check=True)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"An error occurred: {str(e)}")


def terragrunt_destroy(file=None, run_all=True):
    logger.info("Running terragrunt destroy")
    if run_all:
        subprocess_args = [
            "terragrunt",
            "run-all",
            "destroy",
            "-auto-approve",
            "--terragrunt-non-interactive",
        ]
    else:
        subprocess_args = [
            "terragrunt",
            "destroy",
            "-auto-approve",
            "--terragrunt-non-interactive",
        ]

    if file:
        subprocess_args.append("-var-file")
        subprocess_args.append(file)
    try:
        subprocess.run(subprocess_args, check=True)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"An error occurred: {str(e)}")


# This logic is used to get everything ready for terragrunt. This includes:
# 1. Cloning the repository
# 2. Checking out the commit sha
# 3. Installing all asdf plugins under .tool-versions
# 4. Setting ~/.netrc variables
# 5. Copying files and directories from the properties repository to the terragrunt directory
# 6. Assuming the role if the provider is AWS
# 7. Changing the directory to the terragrunt directory
def prepare_for_terragrunt(
    repository: Repo,
    name: str,
    git_token: str,
    commit_sha: str,
    target_environment: str,
    provider_config: dict,
    skip_diff: bool,
    is_pipeline_resources: bool,
    path: str,
    override: dict,
):
    os.chdir(f"{path}/{name}{CODE_GENERATION_DIR_SUFFIX}")

    install_tool_versions(
        file=override["tool_versions_file"],
    )
    set_netrc(password=git_token, machine=override["machine"], login=override["login"])

    # If the Provider is AZURE there is a prequisite requirement of logging into azure
    # i.e. az login, or service principal is already applied to the environment.
    # If the provider is AWS, we need to assume the role for deployment.
    if provider_config:
        if provider_config["provider"] == "aws":
            assume_role(
                provider_config=provider_config,
                repository_name=name,
                target_environment=target_environment,
            )
        if provider_config["provider"] == "az":
            make_configure()
            deploy_remote_state(
                provider_config=provider_config,
            )

    git_diff = check_git_changes(
        repository=repository,
        commit_id=commit_sha,
        main_branch=override["main_branch"],
        directory=override["infrastructure_dir"],
    )

    if skip_diff:
        if is_pipeline_resources:
            exec_dir = f"{override['infrastructure_dir']}"
        else:
            exec_dir = f"{override['environment_dir']}/{target_environment}"
    else:
        if git_diff & is_pipeline_resources:
            if provider_config.provider == "aws":
                exec_dir = f"{override['infrastructure_dir']}"
            else:
                raise RuntimeError(
                    f"Provider: {provider_config.provider}, is_pipeline_resources: {is_pipeline_resources}, and running terragrunt on infrastructure directory: {override['infrastructure_dir']} is not supported"
                )
        elif not git_diff and is_pipeline_resources:
            raise RuntimeError(
                f"No {override['infrastructure_dir']} folder, however, is_pipeline_resources: {is_pipeline_resources}"
            )
        elif git_diff and not is_pipeline_resources:
            raise RuntimeError(
                f"Changes found in {override['infrastructure_dir']} folder, however, is_pipeline_resources: {is_pipeline_resources}"
            )
        else:
            exec_dir = f"{override['environment_dir']}/{target_environment}"

    os.chdir(exec_dir)
