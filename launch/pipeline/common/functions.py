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


logger = logging.getLogger(__name__)

## GIT Specific Functions
def git_clone(target_dir, clone_url: string) -> Repo:
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
        repository = git_clone(
            target_dir=repository_name, 
            clone_url=repository_url
        )
        git_clone(
            target_dir=f"{repository_name}-{override['properties_suffix']}", 
            clone_url=repository_url.replace(repository_name, f"{repository_name}-{override['properties_suffix']}")
        )
    else:
        if not os.path.exists(repository_name.strip()):
            raise RuntimeError(f"Cannot find git repository directories. Please rerun this inside the directory containing the git repository")

    os.chdir(f"{path}/{repository_name}")
    git_checkout(repository=repository, branch=commit_sha)
    install_tool_versions(
        file=override['tool_versions_file'],
    )
    set_netrc(
        password=git_token,
        machine=override['machine'],
        login=override['login']
    )

    git_diff = check_git_changes(
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
        path=f"{directory}/{repository_name}/{infrastructure_dir}"
        properties_path=f"{directory}/{repository_name}-{properties_suffix}/{infrastructure_dir}"
    else:
        path=f"{directory}/{repository_name}/{environment_dir}/{target_environment}"
        properties_path=f"{directory}/{repository_name}-{properties_suffix}/{environment_dir}/{target_environment}"

    copy_files_and_dirs(
        source_dir=properties_path.strip(), 
        destination_dir=path.strip()
    )

    # If the provider is AWS, assume the role
    if provider_config:
        if provider_config.provider == 'aws':
            logger.info(f"Cloud provider: {provider_config.provider}")
            profile = read_key_value_from_file(f"{repository_name}/accounts.json", target_environment)
            aws.assume_role(provider_config.aws.role_to_assume, profile, provider_config.aws.region)
            
    os.chdir(exec_dir)

## Other Functions
# //TODO: verify this function works
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
    excluding_dir_diff = [item.a_path for item in diff if item.a_path.startswith(directory)]
        
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


# //TODO: verify this function works
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

# //TODO: verify this function works
def copy_files_and_dirs(source_dir, destination_dir):
    if not os.path.exists(source_dir):
        raise RuntimeError(f"Source directory not found: {source_dir}")
    if not os.path.exists(destination_dir):
        os.makedirs(destination_dir)

    for item in os.listdir(source_dir):
        source = os.path.join(source_dir, item)
        destination = os.path.join(destination_dir, item)

        if os.path.isdir(source):
            copy_files_and_dirs(source, destination)
        else:
            try:
                shutil.copy2(source, destination)
            except Exception as e:
                raise RuntimeError(f"An error occurred: {str(e)}") from e


# //TODO: verify this function works
def install_tool_versions(file):
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

# //TODO: verify this function works
def set_netrc(password, machine, login):
    logger.info('Setting ~/.netrc variables')
    try:
        with open(os.path.expanduser('~/.netrc'), 'a') as file:
            file.write(f"machine {machine}\n")
            file.write(f"login {login}\n")
            file.write(f"password {password}\n")

        os.chmod(os.path.expanduser('~/.netrc'), 0o600)
    except Exception as e:
        raise RuntimeError(f"An error occurred: {str(e)}")