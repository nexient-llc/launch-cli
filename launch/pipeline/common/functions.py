import logging
import pathlib
import os
import string
import subprocess
import git

from git.repo import Repo

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
def run_terragrunt_init():
    logger.info("Running terragrunt init")
    try:
        subprocess.run(['terragrunt', 'init', '--terragrunt-non-interactive'], check=True)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"An error occurred: {str(e)}")


def terragrunt_plan(file=None):
    logger.info("Running terragrunt plan")
    try:
        if file is None:
            subprocess.run(['terragrunt', 'plan'], check=True)
        else:
            subprocess.run(['terragrunt', 'plan', '-out', file], check=True)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"An error occurred: {str(e)}")


def terragrunt_apply(file=None):
    logger.info("Running terragrunt apply")
    try:
        if file is None:
            subprocess.run(['terragrunt', 'apply', '-auto-approve'], check=True)
        else:
            subprocess.run(['terragrunt', 'apply', '-var-file', file, '-auto-approve'], check=True)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"An error occurred: {str(e)}")


def traverse_terragrunt_dir(type):
    os.chdir(f"{os.environ['CODEBUILD_SRC_DIR']}/{os.environ['GIT_REPO'].rstrip(os.environ['PROPERTIES_REPO_SUFFIX'])}/env/{os.environ['TARGETENV']}/")

    # Dir in format of environment/region/instance
    for dir in glob.glob('./*/*'):
        deploy_dir = dir.lstrip('./')
        region_dir = deploy_dir.split('/')[0]
        aws_profile = get_accounts_profile(f"{os.environ['CODEBUILD_SRC_DIR']}/{os.environ['GIT_REPO'].rstrip(os.environ['PROPERTIES_REPO_SUFFIX'])}/accounts.json", os.environ['TARGETENV'])
        assume_iam_role(os.environ['ROLE_TO_ASSUME'], aws_profile, region_dir)

        os.chdir(f"{os.environ['CODEBUILD_SRC_DIR']}/{os.environ['GIT_REPO'].rstrip(os.environ['PROPERTIES_REPO_SUFFIX'])}/env/{os.environ['TARGETENV']}/{deploy_dir}/")

        for file in glob.glob(f"{os.environ['CODEBUILD_SRC_DIR']}/{os.environ['GIT_REPO'].rstrip(os.environ['PROPERTIES_REPO_SUFFIX'])}{os.environ['PROPERTIES_REPO_SUFFIX']}/env/{os.environ['TARGETENV']}/{deploy_dir}/*"):
            subprocess.run(['cp', '--', file, f"{os.environ['CODEBUILD_SRC_DIR']}/{os.environ['GIT_REPO'].rstrip(os.environ['PROPERTIES_REPO_SUFFIX'])}/env/{os.environ['TARGETENV']}/{deploy_dir}/"], check=True)

        run_terragrunt_init()

        if type == "plan":
            run_terragrunt_plan()
        elif type == "apply":
            run_terragrunt_apply()
        elif type == "pre_deploy":
            run_pre_deploy_test()


## Other Functions
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