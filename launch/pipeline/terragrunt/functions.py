import logging
import os
import subprocess
import os
from launch.pipeline.provider.aws.functions import assume_role
from launch.pipeline.common.functions import copy_files_and_dirs, set_netrc, install_tool_versions, git_clone, git_checkout, check_git_changes


logger = logging.getLogger(__name__)

## Terragrunt Specific Functions
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


# This logic is used to get everything ready for terragrunt. This includes:
# 1. Cloning the repository
# 2. Checking out the commit sha
# 3. Installing all asdf plugins under .tool-versions
# 4. Setting ~/.netrc variables
# 5. Copying files and directories from the properties repository to the terragrunt directory
# 6. Assuming the role if the provider is AWS
# 7. Changing the directory to the terragrunt directory
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
    
    repository=None

    # Get the repository name from the repository url from the last '/' to the '.git'
    repository_name = repository_url.split('/')[-1].split('.git')[0]

    git_clone(
        skip_git=skip_git, 
        target_dir=repository_name, 
        clone_url=repository_url
    ) 
    git_clone(
        skip_git=skip_git,
        target_dir=f"{repository_name}-{override['properties_suffix']}", 
        clone_url=repository_url.replace(repository_name, f"{repository_name}-{override['properties_suffix']}")
    )

    os.chdir(f"{path}/{repository_name}")
    git_checkout(
        repository=repository, 
        branch=commit_sha
    )

    install_tool_versions(
        file=override['tool_versions_file'],
    )
    set_netrc(
        password=git_token,
        machine=override['machine'],
        login=override['login']
    )

    copy_files_and_dirs(
        is_infrastructure=is_infrastructure,
        repository_name=repository_name,
        path=path, 
        target_environment=target_environment, 
        override=override
    )

    # If the Provider is AZURE there is a prequisite requirement of logging into azure
    # i.e. az login, or service principal is already applied to the environment. 
    # If the provider is AWS, we need to assume the role for deployment. 
    if provider_config:
        if provider_config.provider == 'aws':
            assume_role(
                provider_config=provider_config, 
                repository_name=repository_name, 
                target_environment=target_environment
            )

    git_diff = check_git_changes(
        repository=repository,
        commit_id=commit_sha, 
        main_branch=override['main_branch'], 
        directory=override['infrastructure_dir']
    )
    if git_diff & is_infrastructure:
        #TODO: this needs more expanision for various resources under internals for aws
        if provider_config.provider == 'aws':
            exec_dir = f"{override['infrastructure_dir']}"
        else:
            raise RuntimeError(f"Provider: {provider_config.provider}, is_infrastructure: {is_infrastructure}, and running terragrunt on infrastructure directory: {override['infrastructure_dir']} is not supported")
    elif not git_diff and  is_infrastructure:
        raise RuntimeError(f"No {override['infrastructure_dir']} folder, however, is_infrastructure: {is_infrastructure}")
    elif git_diff and not is_infrastructure:
        raise RuntimeError(f"Changes found in {override['infrastructure_dir']} folder, however, is_infrastructure: {is_infrastructure}")
    else:
        exec_dir = f"{override['environment_dir']}/{target_environment}"
    os.chdir(exec_dir)
