import json
import logging
import shutil
from pathlib import Path
from typing import IO, Any

import click

from launch import (
    BUILD_DEPEPENDENCIES_DIR,
    CODE_GENERATION_DIR_SUFFIX,
    GITHUB_ORG_NAME,
    INIT_BRANCH,
    MAIN_BRANCH,
)
from launch.cli.github.access.commands import set_default
from launch.github.auth import get_github_instance
from launch.github.repo import create_repository, repo_exist
from launch.local_repo.repo import checkout_branch, clone_repository, push_branch
from launch.service.common import (
    copy_and_render_templates,
    copy_properties_files,
    create_directories,
    input_data_validation,
    list_jinja_templates,
    write_text,
)

logger = logging.getLogger(__name__)


@click.command()
@click.option(
    "--organization",
    default=GITHUB_ORG_NAME,
    help="GitHub organization containing your repository. Defaults to the nexient-llc organization.",
)
@click.option("--name", required=True, help="Name of the service to  be created.")
@click.option(
    "--description",
    default="Service created with launch-cli.",
    help="A short description of the repository.",
)
@click.option(
    "--public",
    is_flag=True,
    default=False,
    help="The visibility of the repository.",
)
@click.option(
    "--visibility",
    default="private",
    help="The visibility of the repository. Can be one of: public, private.",
)
@click.option(
    "--main-branch",
    default=MAIN_BRANCH,
    help="The name of the main branch.",
)
@click.option(
    "--remote-branch",
    default=INIT_BRANCH,
    help="The name of the remote branch when creating/updating a repository.",
)
@click.option(
    "--in-file",
    required=True,
    type=click.File("r"),
    help="Inputs to be used with the skeleton during creation.",
)
@click.option(
    "--skip-commit",
    is_flag=True,
    default=False,
    help="If set, it will skip commiting the local changes.",
)
@click.option(
    "--git-message",
    default="Initial commit",
    help="The git commit message to use when creating a commit. Defaults to 'Initial commit'.",
)
@click.option(
    "--dry-run",
    is_flag=True,
    default=False,
    help="Perform a dry run that reports on what it would do, but does not create webhooks.",
)
@click.pass_context
# TODO: Optimize this function and logic
# Ticket: 1633
def create(
    context: click.Context,
    organization: str,
    name: str,
    description: str,
    public: bool,
    visibility: str,
    main_branch: str,
    remote_branch: str,
    in_file: IO[Any],
    skip_commit: bool,
    git_message: str,
    dry_run: bool,
):
    """Creates a new service."""

    if dry_run:
        click.secho("Performing a dry run, nothing will be created", fg="yellow")
        # TODO: add a dry run for the create command
        return

    service_path = f"{Path.cwd()}/{name}"
    input_data = json.load(in_file)
    input_data = input_data_validation(input_data)

    g = get_github_instance()

    if repo_exist(name=name, g=g):
        click.secho(
            "Repo already exists remotely. Please use launch service update, to update a service.",
            fg="red",
        )
        return

    service_repo = create_repository(
        g=g,
        organization=organization,
        name=name,
        description=description,
        public=public,
        visibility=visibility,
    )
    context.invoke(
        set_default,
        organization=organization,
        repository_name=name,
        dry_run=dry_run,
    )

    repository = clone_repository(
        repository_url=service_repo.clone_url, target=name, branch=main_branch
    )
    checkout_branch(
        repository=repository,
        init_branch=remote_branch,
        main_branch=main_branch,
        new_branch=True,
    )

    create_directories(
        base_path=f"{service_path}/{BUILD_DEPEPENDENCIES_DIR}",
        platform_data=input_data["platform"],
    )
    input_data["platform"] = copy_properties_files(
        dest_base_path=f"{service_path}/{BUILD_DEPEPENDENCIES_DIR}/",
        platform_data=input_data["platform"],
    )
    write_text(
        data=input_data,
        path=Path(f"{service_path}/.launch_config"),
    )
    if not skip_commit:
        push_branch(repository=repository, branch=remote_branch, commit_msg=git_message)


@click.command()
@click.option(
    "--organization",
    default=GITHUB_ORG_NAME,
    help="GitHub organization containing your repository. Defaults to the nexient-llc organization.",
)
@click.option("--name", required=True, help="Name of the service to  be created.")
@click.option(
    "--main-branch",
    default=MAIN_BRANCH,
    help="The name of the main branch.",
)
@click.option(
    "--remote-branch",
    default=INIT_BRANCH,
    help="The name of the remote branch when creating/updating a repository.",
)
@click.option(
    "--in-file",
    required=True,
    type=click.File("r"),
    help="Inputs to be used with the skeleton during creation.",
)
@click.option(
    "--skip-git",
    is_flag=True,
    default=False,
    help="If set, it will ignore cloning and checking out the git repository.",
)
@click.option(
    "--skip-commit",
    is_flag=True,
    default=False,
    help="If set, it will skip commiting the local changes.",
)
@click.option(
    "--git-message",
    default="bot: launch service update commit",
    help="The git commit message to use when creating a commit. Defaults to 'bot: launch service update commit'.",
)
@click.option(
    "--dry-run",
    is_flag=True,
    default=False,
    help="Perform a dry run that reports on what it would do, but does not create webhooks.",
)
def update(
    organization: str,
    name: str,
    main_branch: str,
    remote_branch: str,
    in_file: IO[Any],
    skip_git: bool,
    skip_commit: bool,
    git_message: str,
    dry_run: bool,
):
    """Updates a service."""

    if dry_run:
        click.secho("Performing a dry run, nothing will be created", fg="yellow")
        # TODO: add a dry run for the update command
        return

    service_path = f"{Path.cwd()}/{name}"
    if not Path(service_path).exists():
        click.secho(f"Error: Path {service_path} does not exist.", fg="red")
        return

    input_data = json.load(in_file)
    input_data = input_data_validation(input_data)

    g = get_github_instance()

    if not repo_exist(name=name, g=g):
        click.secho(
            "Repo does not exist remotely. Please use launch service create to create a new service.",
            fg="red",
        )
        return

    service_repo = g.get_repo(f"{organization}/{name}")

    if not skip_git:
        repository = clone_repository(
            repository_url=service_repo.clone_url, target=name, branch=main_branch
        )
        checkout_branch(
            repository=repository,
            init_branch=remote_branch,
            main_branch=main_branch,
            new_branch=True,
        )
    else:
        try:
            shutil.rmtree(f"{service_path}/{BUILD_DEPEPENDENCIES_DIR}")
        except FileNotFoundError:
            logger.info(
                f"Directory not found when trying to delete: {service_path}/{BUILD_DEPEPENDENCIES_DIR}"
            )

    create_directories(
        base_path=f"{service_path}/{BUILD_DEPEPENDENCIES_DIR}",
        platform_data=input_data["platform"],
    )
    input_data["platform"] = copy_properties_files(
        dest_base_path=f"{service_path}/{BUILD_DEPEPENDENCIES_DIR}/",
        platform_data=input_data["platform"],
    )
    write_text(
        data=input_data,
        path=Path(f"{service_path}/.launch_config"),
    )
    if not skip_commit:
        push_branch(repository=repository, branch=remote_branch, commit_msg=git_message)


@click.command()
@click.option(
    "--organization",
    default=GITHUB_ORG_NAME,
    help=f"GitHub organization containing your repository. Defaults to the {GITHUB_ORG_NAME} organization.",
)
@click.option("--name", required=True, help="Name of the service to  be created.")
@click.option(
    "--service-branch",
    default=MAIN_BRANCH,
    help="The name of the service branch.",
)
@click.option(
    "--skip-git",
    is_flag=True,
    default=False,
    help="If set, it will ignore cloning and checking out the git repository and it's properties.",
)
@click.option(
    "--work-dir",
    default=Path.cwd(),
    help="",
)
@click.option(
    "--dry-run",
    is_flag=True,
    default=False,
    help="Perform a dry run that reports on what it would do, but does not create webhooks.",
)
# TODO: Optimize this function and logic
# Ticket: 1633
def generate(
    organization: str,
    name: str,
    service_branch: str,
    skip_git: bool,
    work_dir: Path,
    dry_run: bool,
):
    """Dynamically generates terragrunt files based off a service."""

    if dry_run:
        click.secho("Performing a dry run, nothing will be created", fg="yellow")

    singlerun_path = f"{work_dir}/{name}{CODE_GENERATION_DIR_SUFFIX}"
    service_path = f"{Path.cwd()}/{name}"

    g = get_github_instance()
    repo = g.get_repo(f"{organization}/{name}")

    if not skip_git:
        clone_repository(
            repository_url=repo.clone_url,
            target=f"{work_dir}/{name}",
            branch=service_branch,
        )
        clone_repository(
            repository_url=input_data["skeleton"]["url"],
            target=singlerun_path,
            branch=input_data["skeleton"]["tag"],
        )

    with open(f"{work_dir}/{name}/.launch_config", "r") as f:
        input_data = json.load(f)

    shutil.copytree(
        f"{service_path}/{BUILD_DEPEPENDENCIES_DIR}",
        f"{singlerun_path}/{BUILD_DEPEPENDENCIES_DIR}",
        dirs_exist_ok=True,
    )

    # Creating directories and copying properties files
    create_directories(singlerun_path, input_data["platform"])
    copy_properties_files(
        base_path=singlerun_path, platform_data=input_data["platform"]
    )

    # Placing Jinja templates
    template_paths, jinja_paths = list_jinja_templates(
        singlerun_path / Path(f"{BUILD_DEPEPENDENCIES_DIR}/jinja2")
    )
    copy_and_render_templates(
        base_dir=singlerun_path,
        template_paths=template_paths,
        modified_paths=jinja_paths,
        context_data={"data": {"config": input_data}},
    )

    # Remove the .launch directory
    shutil.rmtree(f"{singlerun_path}/.launch")


@click.command()
@click.option("--name", required=True, help="Name of the service to  be created.")
@click.option(
    "--work-dir",
    default=Path.cwd(),
    help="",
)
@click.option(
    "--dry-run",
    is_flag=True,
    default=False,
    help="Perform a dry run that reports on what it would do, but does not create webhooks.",
)
def cleanup(
    name: str,
    work_dir: Path,
    dry_run: bool,
):
    """Cleans up launch-cli reources that are created from code generation."""

    if dry_run:
        click.secho("Performing a dry run, nothing will be cleaned", fg="yellow")
        return

    try:
        shutil.rmtree(f"{work_dir}/{name}{CODE_GENERATION_DIR_SUFFIX}")
        logger.info(f"Deleted {work_dir}/{name}{CODE_GENERATION_DIR_SUFFIX} directory.")
    except FileNotFoundError:
        click.secho(
            f"Repository not found: {work_dir}/{name}{CODE_GENERATION_DIR_SUFFIX}",
            fg="red",
        )
