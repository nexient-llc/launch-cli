import logging
import os
import string
import subprocess
import git
import json

from git.repo import Repo
import shutil
import os
from launch.pipeline.provider import aws
import launch.pipeline.common.functions as common


logger = logging.getLogger(__name__)

## Terragrunt Specific Functions
# //TODO: verify this function works
def terragrunt_init(run_all=True):
    logger.info("Running terragrunt init")
    if run_all:
        subprocess_args = ['terragrunt', 'run-all', 'init', '--terragrunt-non-interactive']
    else:
        subprocess_args = ['terragrunt', 'init', '--terragrunt-non-interactive']
    
    try:
        subprocess.run(subprocess_args, check=True)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"An error occurred: {str(e)}")

# //TODO: verify this function works
def terragrunt_plan(file=None, run_all=True):
    logger.info("Running terragrunt plan")
    if run_all:
        subprocess_args = ['terragrunt', 'run-all', 'plan']
    else:
        subprocess_args = ['terragrunt', 'plan']

    if file:
        subprocess_args.append('-out')
        subprocess_args.append(file)
    try:
        subprocess.run(subprocess_args, check=True)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"An error occurred: {str(e)}")

# //TODO: verify this function works
def terragrunt_apply(file=None, run_all=True):
    logger.info("Running terragrunt apply")
    if run_all:
        subprocess_args = ['terragrunt', 'run-all', 'apply', '-auto-approve']
    else:
        subprocess_args = ['terragrunt', 'apply', '-auto-approve']

    if file:
        subprocess_args.append('-var-file')
        subprocess_args.append(file)
    try:
        subprocess.run(subprocess_args, check=True)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"An error occurred: {str(e)}")

# //TODO: verify this function works
def prepare_for_terragrunt(
        repository_url,
        git_token,
        commit_sha,
        target_environment,
        provider_config,
        skip_git,
        is_infrastructure,
        path,
        override
    ):
    
    # Get the repository name from the repository url from the last '/' to the '.git'
    repository_name = repository_url.split('/')[-1].split('.git')[0]

    if not skip_git:
        repository = common.git_clone(
            target_dir=repository_name, 
            clone_url=repository_url
        )
        common.git_clone(
            target_dir=f"{repository_name}-{override['properties_suffix']}", 
            clone_url=repository_url.replace(repository_name, f"{repository_name}-{override['properties_suffix']}")
        )
    else:
        if not os.path.exists(repository_name.strip()):
            raise RuntimeError(f"Cannot find git repository directories. Please rerun this inside the directory containing the git repository")

    os.chdir(f"{path}/{repository_name}")
    common.git_checkout(repository=repository, branch=commit_sha)
    common.install_tool_versions(
        file=override['tool_versions_file'],
    )
    common.set_netrc(
        password=git_token,
        machine=override['machine'],
        login=override['login']
    )

    git_diff = common.check_git_changes(
        repository=repository,
        commit_id=commit_sha, 
        main_branch=override['main_branch'], 
        directory=override['infrastructure_dir']
    )
    
    if git_diff & is_infrastructure:
        #TODO: this needs more expanision for various resources under internals
        exec_dir = f"{override['infrastructure_dir']}"
    elif not git_diff and  is_infrastructure:
        raise RuntimeError(f"No  {override['infrastructure_dir']} folder, however, is_infrastructure: {is_infrastructure}")
    elif git_diff and not is_infrastructure:
        raise RuntimeError(f"Changes found in {override['infrastructure_dir']} folder, however, is_infrastructure: {is_infrastructure}")
    else:
        exec_dir = f"{override['environment_dir']}/{target_environment}"

    # Copy files and directories from the properties repository to the terragrunt directory
    if is_infrastructure:
        path=f"{path}/{repository_name}/{override['infrastructure_dir']}"
        properties_path=f"{path}/{repository_name}-{override['properties_suffix']}/{override['infrastructure_dir']}"
    else:
        path=f"{path}/{repository_name}/{override['environment_dir']}/{target_environment}"
        properties_path=f"{path}/{repository_name}-{override['properties_suffix']}/{override['environment_dir']}/{target_environment}"

    common.copy_files_and_dirs(
        source_dir=properties_path.strip(), 
        destination_dir=path.strip()
    )

    # If the provider is AWS, assume the role
    if provider_config:
        if provider_config.provider == 'aws':
            logger.info(f"Cloud provider: {provider_config.provider}")
            profile = common.read_key_value_from_file(f"{repository_name}/accounts.json", target_environment)
            aws.assume_role(provider_config.aws.role_to_assume, profile, provider_config.aws.region)
            
    os.chdir(exec_dir)
