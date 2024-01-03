import logging
import pathlib
import os
import string
import subprocess
import git

from git.repo import Repo
import shutil
import os

logger = logging.getLogger(__name__)

## GIT Specific Functions
def git_clone(clone_url: string, target_dir='.') -> Repo:
    try:
        repository = Repo.clone_from(clone_url, target_dir)
        logger.info(f"Repository {clone_url} cloned successfully to {target_dir}")
    except git.GitCommandError as e:
        raise RuntimeError(f"An error occurred while cloning the repository: {clone_url}") from e
    return repository


def git_checkout(repository: Repo, branch=None, new_branch=False):
    if branch:
        try:
            if new_branch:
                repository.git.checkout('-b', branch)
                logger.info(f"Checked out new branch: {branch}")
            else:
                repository.git.checkout(branch)
                logger.info(f"Checked out branch: {branch}")
        except git.GitCommandError as e:
            raise RuntimeError(f"An error occurred while checking out {branch}:  {str(e)}") from e


## Terragrunt Specific Functions
# //TODO: verify this function works
def terragrunt_init(run_all=True):
    logger.info("Running terragrunt init")
    try:
        if run_all:
            subprocess.run(['terragrunt', 'run-all', 'init', '--terragrunt-non-interactive'], check=True)
        else:
            subprocess.run(['terragrunt', 'init', '--terragrunt-non-interactive'], check=True)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"An error occurred: {str(e)}")

# //TODO: verify this function works
def terragrunt_plan(file=None, run_all=True):
    logger.info("Running terragrunt plan")
    if run_all:
        subprocess_args = ['terragrunt', 'run_all', 'plan']
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
        subprocess_args = ['terragrunt', 'run_all', 'apply', '-auto-approve']
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
        repository,
        properties_suffix,
        target_environment,
        provider_config=None,
        directory=os.path.expanduser("~"),
    ):

    terragrunt_dir=f"{directory}/{repository.rstrip({properties_suffix})}/env/{target_environment}"
    properties_terragrunt_dir=f"{directory}/{repository.rstrip(properties_suffix)}{properties_suffix}/env/{target_environment}"

    copy_files_and_dirs(terragrunt_dir, properties_terragrunt_dir)

    if provider_config.provider == 'aws':
        aws_profile = get_accounts_profile(f"{directory}/{repository.rstrip(properties_suffix)}/accounts.json", target_environment)
        assume_iam_role(cloud_config.aws.role_to_assume, aws_profile, cloud_config.aws.region)



def copy_files_and_dirs(src_dir, dst_dir):
    if not os.path.exists(src_dir):
        print(f"The source directory {src_dir} does not exist.")
        return

    for item in os.listdir(src_dir):
        src_path = os.path.join(src_dir, item)
        dst_path = os.path.join(dst_dir, item)

        if os.path.isdir(src_path):
            if not os.path.exists(dst_path):
                shutil.copytree(src_path, dst_path)
            else:
                copy_files_and_dirs(src_path, dst_path)
        else:
            shutil.copy2(src_path, dst_path)

## Other Functions
# //TODO: verify this function works
def install_tool_versions(file='.tool-versions'):
    logger.info('Installing all asdf plugins under .tool-versions')
    try:
        os.chdir(dir)
        with open(file, 'r') as file:
            lines = file.readlines()

        for line in lines:
            plugin = line.split()[0]
            subprocess.run(['asdf', 'plugin', 'add', plugin], check=True)

        subprocess.run(['asdf', 'install'], check=True)
    except Exception as e:
        raise RuntimeError(f"An error occurred with asdf install {file}: {str(e)}") from e

# //TODO: verify this function works
def set_netrc(password, machine='github.com', login='nobody'):
    logger.info('Setting ~/.netrc variables')
    try:
        with open(os.path.expanduser('~/.netrc'), 'a') as file:
            file.write(f"machine {machine}\n")
            file.write(f"login {login}\n")
            file.write(f"password {password}\n")

        os.chmod(os.path.expanduser('~/.netrc'), 0o600)
    except Exception as e:
        raise RuntimeError(f"An error occurred: {str(e)}")