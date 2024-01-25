import logging
import os
import string
import subprocess
import git
import json
from git.repo import Repo


logger = logging.getLogger(__name__)

## GIT Specific Functions
def git_clone(skip_git, target_dir, clone_url: string) -> Repo:
    if not skip_git:
        try:
            logger.info(f"Cloning repository: {clone_url} into {target_dir}")
            repository = Repo.clone_from(clone_url, target_dir)
        except git.GitCommandError as e:
            logger.error(f"Error occurred while cloning the repository: {clone_url}, Error: {e}")
            raise RuntimeError(f"An error occurred while cloning the repository: {clone_url}") from e
        return repository
    else:
        try:
            logger.info(f"Getting repository: {clone_url} into {target_dir}")
            if clone_url.endswith('.git'):
                clone_url = clone_url[:-4]
            repo_name = clone_url.split('/')[-1:]
            repository = Repo(f"./{repo_name[0]}")
        except (git.GitCommandError, git.exc.NoSuchPathError) as e:
            logger.error(f"Error occurred while getting the repository: {clone_url}, Error: {e}")
            raise RuntimeError(f"An error occurred while getting the repository: {clone_url}") from e
        return repository


def git_checkout(skip_git, repository: Repo, branch=None, new_branch=False) -> None:
    if skip_git:
        return None
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


## Other Functions
def check_git_changes( 
        repository, 
        commit_id, 
        main_branch, 
        directory
    ) -> bool:

    logger.info(f"Checking if git changes are exclusive to: {directory}")
    origin = repository.remote(name='origin')
    origin.fetch()
    
    commit_main=repository.commit(f"origin/{main_branch}")
    
    # Check if the PR commit hash is the same as the commit sha of the main branch
    if commit_id == repository.rev_parse(f"origin/{main_branch}"):
        logger.info(f"Commit hash is the same as origin/{main_branch}")
        commit_compare=repository.commit(f"origin/{main_branch}^")
    # PR commit sha is not the same as the commit sha of the main branch. Thus we want whats been changed since because
    # terragrunt will apply all changes.
    else:
        commit_compare=repository.commit(commit_id)
    
    # Get the diff between of the last commit only inside the infrastructure directory
    exclusive_dir_diff = commit_compare.diff(commit_main, paths=directory, name_only=True)
    # Get the diff between of the last commit only outside the infrastructure directory
    diff = commit_compare.diff(commit_main, name_only=True)
    excluding_dir_diff = [item.a_path for item in diff if not item.a_path.startswith(directory)]
        
    # If there are no git changes, return false.
    if not exclusive_dir_diff:
        logger.info(f"No git changes found in dir: {directory}")
        return False
    else:
        # If both are true, we want to throw to prevent simultaneous infrastructure and service changes.
        if excluding_dir_diff:
            raise RuntimeError(f"Changes found in both inside and outside dir: {directory}")
        # If only the infrastructure directory has changes, return true.
        else:
            logger.info(f"Git changes only found in folder: {directory}")
            return True


def read_key_value_from_file(file, key) -> string:
    try:
        with open(file) as blob:
            data = json.load(blob)
            value = data.get(key)
            if value:
                logger.info(f"Found key, value: {key}, {value}")
                return value
            else:
                raise KeyError(f"No key found: {key}")
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {file}")


def install_tool_versions(file) -> None:
    logger.info('Installing all asdf plugins under .tool-versions')
    try:
        with open(file, 'r') as file:
            lines = file.readlines()

        for line in lines:
            plugin = line.split()[0]
            subprocess.run(['asdf', 'plugin', 'add', plugin], check=True)

        subprocess.run(['asdf', 'install'], check=True)
    except Exception as e:
        raise RuntimeError(f"An error occurred with asdf install {file}: {str(e)}") from e


def set_netrc(password, machine, login) -> None:
    logger.info('Setting ~/.netrc variables')
    try:
        with open(os.path.expanduser('~/.netrc'), 'a') as file:
            file.write(f"machine {machine}\n")
            file.write(f"login {login}\n")
            file.write(f"password {password}\n")

        os.chmod(os.path.expanduser('~/.netrc'), 0o600)
    except Exception as e:
        raise RuntimeError(f"An error occurred: {str(e)}")