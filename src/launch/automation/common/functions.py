import itertools
import json
import logging
import os
import pathlib
import shutil
import string
import subprocess

import git
from git.repo import Repo
from ruamel.yaml import YAML

from launch import DISCOVERY_FORBIDDEN_DIRECTORIES

logger = logging.getLogger(__name__)


## GIT Specific Functions
def git_clone(skip_git: str, target_dir: str, clone_url: str) -> Repo:
    if not skip_git:
        try:
            logger.info(f"Cloning repository: {clone_url} into {target_dir}")
            repository = Repo.clone_from(clone_url, target_dir)
        except git.GitCommandError as e:
            logger.error(
                f"Error occurred while cloning the repository: {clone_url}, Error: {e}"
            )
            raise RuntimeError(
                f"An error occurred while cloning the repository: {clone_url}"
            ) from e
        return repository
    else:
        try:
            logger.info(f"Getting repository: {clone_url} into {target_dir}")
            if clone_url.endswith(".git"):
                clone_url = clone_url[:-4]
            repo_name = clone_url.split("/")[-1:]
            repository = Repo(f"./{repo_name[0]}")
        except (git.GitCommandError, git.exc.NoSuchPathError) as e:
            logger.error(
                f"Error occurred while getting the repository: {clone_url}, Error: {e}"
            )
            raise RuntimeError(
                f"An error occurred while getting the repository: {clone_url}"
            ) from e
        return repository


def git_checkout(skip_git, repository: Repo, branch=None, new_branch=False) -> None:
    if skip_git:
        return None
    if branch:
        try:
            if new_branch:
                repository.git.checkout("-b", branch)
                logger.info(f"Checked out new branch: {branch}")
            else:
                repository.git.checkout(branch)
                logger.info(f"Checked out branch: {branch}")
        except git.GitCommandError as e:
            raise RuntimeError(
                f"An error occurred while checking out {branch}:  {str(e)}"
            ) from e


## Other Functions
def check_git_changes(repository, commit_id, main_branch, directory) -> bool:
    logger.info(f"Checking if git changes are exclusive to: {directory}")
    origin = repository.remote(name="origin")
    origin.fetch()

    commit_main = repository.commit(f"origin/{main_branch}")

    # Check if the PR commit hash is the same as the commit sha of the main branch
    if commit_id == repository.rev_parse(f"origin/{main_branch}"):
        logger.info(f"Commit hash is the same as origin/{main_branch}")
        commit_compare = repository.commit(f"origin/{main_branch}^")
    # PR commit sha is not the same as the commit sha of the main branch. Thus we want whats been changed since because
    # terragrunt will apply all changes.
    else:
        commit_compare = repository.commit(commit_id)

    # Get the diff between of the last commit only inside the infrastructure directory
    exclusive_dir_diff = commit_compare.diff(
        commit_main, paths=directory, name_only=True
    )
    # Get the diff between of the last commit only outside the infrastructure directory
    diff = commit_compare.diff(commit_main, name_only=True)
    excluding_dir_diff = [
        item.a_path for item in diff if not item.a_path.startswith(directory)
    ]

    # If there are no git changes, return false.
    if not exclusive_dir_diff:
        logger.info(f"No git changes found in dir: {directory}")
        return False
    else:
        # If both are true, we want to throw to prevent simultaneous infrastructure and service changes.
        if excluding_dir_diff:
            raise RuntimeError(
                f"Changes found in both inside and outside dir: {directory}"
            )
        # If only the infrastructure directory has changes, return true.
        else:
            logger.info(f"Git changes only found in folder: {directory}")
            return True


def read_key_value_from_file(file: str, key: str) -> string:
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


def install_tool_versions(file: str) -> None:
    logger.info("Installing all asdf plugins under .tool-versions")
    try:
        with open(file, "r") as file:
            lines = file.readlines()

        for line in lines:
            plugin = line.split()[0]
            subprocess.run(["asdf", "plugin", "add", plugin])

        subprocess.run(["asdf", "install"])
    except Exception as e:
        raise RuntimeError(
            f"An error occurred with asdf install {file}: {str(e)}"
        ) from e


def set_netrc(password: str, machine: str, login: str) -> None:
    logger.info("Setting ~/.netrc variables")
    try:
        with open(os.path.expanduser("~/.netrc"), "a") as file:
            file.write(f"machine {machine}\n")
            file.write(f"login {login}\n")
            file.write(f"password {password}\n")

        os.chmod(os.path.expanduser("~/.netrc"), 0o600)
    except Exception as e:
        raise RuntimeError(f"An error occurred: {str(e)}")


def make_configure() -> None:
    logger.info(f"Running make configure")
    try:
        subprocess.run(["make", "configure"], check=True)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"An error occurred: {str(e)}") from e


def deploy_remote_state(provider_config: dict) -> None:
    run_list = ["make"]

    if provider_config["az"].get("name_prefix"):
        run_list.append(f"NAME_PREFIX={provider_config['az'].get('name_prefix')}")
    if provider_config["az"].get("region"):
        run_list.append(f"REGION={provider_config['az'].get('region')}")
    if provider_config["az"].get("environment"):
        run_list.append(f"ENVIRONMENT={provider_config['az'].get('environment')}")
    if provider_config["az"].get("env_instance"):
        run_list.append(f"ENV_INSTANCE={provider_config['az'].get('env_instance')}")
    if provider_config["az"].get("container_name"):
        run_list.append(f"CONTAINER_NAME={provider_config['az'].get('container_name')}")
    if provider_config["az"].get("storage_account_name"):
        run_list.append(
            f"STORAGE_ACCOUNT_NAME={provider_config['az'].get('storage_account_name')}"
        )
    if provider_config["az"].get("resource_group_name"):
        run_list.append(
            f"RESOURCE_GROUP_NAME={provider_config['az'].get('resource_group_name')}"
        )

    run_list.append("terragrunt/remote_state/azure")

    logger.info(f"Running {run_list}")
    try:
        subprocess.run(run_list, check=True)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"An error occurred: {str(e)}") from e


def discover_files(
    root_path: pathlib.Path,
    filename_partial: str = "",
    forbidden_directories: list[str] = None,
) -> list[pathlib.Path]:
    """Recursively discovers files underneath a top level root_path that match a partial name.

    Args:
        root_path (pathlib.Path): Top level directory to search
        filename_partial (str, optional): Case-insensitive part of the filename to search. Defaults to "", which will return all files. This partial search uses an 'in' expression, do not use a wildcard.
        forbidden_directories (list[str], optional): List of strings to match in directory names that will not be traversed. Defaults to None, which forbids traversal of some common directories (.git, .terraform, etc.). To search all directories, pass an empty list.

    Returns:
        list[pathlib.Path]: List of pathlib.Path objects for files matching filename_partial.
    """
    if forbidden_directories is None:
        forbidden_directories = DISCOVERY_FORBIDDEN_DIRECTORIES

    directories = [
        d
        for d in root_path.iterdir()
        if d.is_dir() and not d.name.lower() in forbidden_directories
    ]
    files = [
        f
        for f in root_path.iterdir()
        if not f.is_dir() and filename_partial in f.name.lower()
    ]
    files.extend(
        list(
            itertools.chain.from_iterable(
                [
                    discover_files(
                        root_path=d,
                        filename_partial=filename_partial,
                        forbidden_directories=forbidden_directories,
                    )
                    for d in directories
                ]
            )
        )
    )
    return files


def discover_directories(
    root_path: pathlib.Path,
    dirname_partial: str = "",
    forbidden_directories: list[str] = None,
) -> list[pathlib.Path]:
    """Recursively discovers subdirectories underneath a top level root_path that match a partial name. If a subdirectory doesn't match that partial name, none of its children will be searched.

    Args:
        root_path (pathlib.Path): Top level directory to search
        dirname_partial (str, optional): Case-insensitive part of the subdirectory name match. Defaults to "", which will return all subdirectories. This partial search uses an 'in' expression, do not use a wildcard.
        forbidden_directories (list[str], optional): List of strings to match in directory names that will not be traversed. Defaults to None, which forbids traversal of some common directories (.git, .terraform, etc.). To search all directories, pass an empty list.

    Returns:
        list[pathlib.Path]: List of pathlib.Path objects for files matching filename_partial.
    """

    if forbidden_directories is None:
        forbidden_directories = DISCOVERY_FORBIDDEN_DIRECTORIES

    directories = [
        d
        for d in root_path.iterdir()
        if d.is_dir()
        and dirname_partial in d.name
        and not d.name.lower() in forbidden_directories
    ]
    directories.extend(
        list(
            itertools.chain.from_iterable(
                [
                    discover_directories(
                        root_path=d,
                        dirname_partial=dirname_partial,
                        forbidden_directories=forbidden_directories,
                    )
                    for d in directories
                ]
            )
        )
    )
    return directories


def load_yaml(yaml_file: pathlib.Path) -> dict:
    """Instantiates a YAML parser and loads the content of a file containing YAML data.

    Args:
        yaml_file (pathlib.Path): Path to the YAML file

    Returns:
        dict: Dictionary containing the YAML structure
    """
    yaml_parser = YAML(typ="safe")
    yaml_contents: dict = yaml_parser.load(stream=yaml_file)
    return yaml_contents


def unpack_archive(
    archive_path: pathlib.Path,
    destination: pathlib.Path = pathlib.Path.cwd(),
    format_override: str = None,
) -> None:
    """Unpacks a single archive file to a desired destination directory. If the destination exists, it must be a directory. If it does not exist, it will be created.

    Args:
        archive_path (pathlib.Path): Path to a compressed archive
        destination (pathlib.Path, optional): Folder into which the archive will unpack, maintaining its internal packed structure. Defaults to pathlib.Path.cwd().
        format_override (str, optional): Override format detection with a particular format (one of "zip", "tar", "gztar", "bztar", or "xztar"). Defaults to None, which will detect format based on the filename.

    Raises:
        FileNotFoundError: Raised when the archive cannot be found
        FileExistsError: Raised when the destination exists but is not a directory.
    """
    if not archive_path.exists():
        raise FileNotFoundError(f"Supplied archive path {archive_path} does not exist!")

    if destination.exists() and not destination.is_dir():
        raise FileExistsError(
            f"Supplied destination {destination} exists but is not a directory!"
        )
    destination.mkdir(parents=True, exist_ok=True)

    if format_override is None:
        logger.debug(f"Unpacking archive {archive_path} to {destination}")
        shutil.unpack_archive(filename=archive_path, extract_dir=destination)
    else:
        logger.debug(
            f"Unpacking archive {archive_path} to {destination} with overridden format {format_override}"
        )
        shutil.unpack_archive(
            filename=archive_path, extract_dir=destination, format=format_override
        )
