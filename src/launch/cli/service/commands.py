import json
import logging
import os
import re
import shutil
import subprocess
from pathlib import Path
from typing import IO, Any

import click
from jinja2 import Environment, FileSystemLoader

from launch import (
    GITHUB_ORG_NAME,
    INIT_BRANCH,
    MAIN_BRANCH,
    SERVICE_SKELETON,
    SKELETON_BRANCH,
)
from launch.cli.github.access.commands import set_default
from launch.github.auth import get_github_instance
from launch.github.repo import clone_repository, create_repository, does_repo_exist
from launch.local_repo.repo import checkout_branch, push_branch
from launch.service.common import (
    copy_and_render_templates,
    copy_properties_files,
    create_directories,
    list_jinja_templates,
    write_launch_config,
)

logger = logging.getLogger(__name__)


@click.command()
@click.option(
    "--organization",
    default=GITHUB_ORG_NAME,
    help="GitHub organization containing your repository. Defaults to the nexient-llc organization.",
)
@click.option(
    "--name", required=True, help="(Required) Name of the service to  be created."
)
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
    "--init-branch",
    default=INIT_BRANCH,
    help="The name of the initial branch to create on the repository for a PR.",
)
@click.option(
    "--in-file",
    required=True,
    type=click.File("r"),
    help="(Required) Inputs to be used with the skeleton during creation.",
)
@click.option(
    "--new-service",
    is_flag=True,
    default=False,
    help="Perform a dry run that reports on what it would do, but does not create webhooks.",
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
    init_branch: str,
    in_file: IO[Any],
    new_service: bool,
    dry_run: bool,
):
    """Creates a new service."""

    if dry_run:
        click.secho("Performing a dry run, nothing will be created", fg="yellow")

    if does_repo_exist and new_service:
        click.secho(
            "Repo was already exists and the --new-service flag is specified. Please remove this flag to update a service.",
            fg="red",
        )

    service_path = f"{os.getcwd()}/{name}"
    input_data = json.load(in_file)
    input_data["skeleton"]["url"] = SERVICE_SKELETON
    input_data["skeleton"]["tag"] = SKELETON_BRANCH

    g = get_github_instance()

    if new_service:
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
    else:
        service_repo = g.get_repo(f"{organization}/{name}")

    clone_repository(
        repository_url=service_repo.clone_url, target=name, branch=main_branch
    )

    checkout_branch(
        path=service_path,
        init_branch=init_branch,
        main_branch=main_branch,
        new_branch=True,
    )

    create_directories(base_path=service_path, platform_data=input_data["platform"])
    input_data["platform"] = copy_properties_files(
        base_path=service_path, platform_data=input_data["platform"]
    )
    write_launch_config(
        data=json.dumps(input_data, indent=4),
        path=Path(f"{service_path}/.launch_config"),
    )
    push_branch(path=service_path, init_branch=init_branch, commit_msg="Initial commit")


@click.command()
@click.option(
    "--organization",
    default=GITHUB_ORG_NAME,
    help="GitHub organization containing your repository. Defaults to the nexient-llc organization.",
)
@click.option(
    "--name", required=True, help="(Required) Name of the service to  be created."
)
@click.option(
    "--skeleton-url",
    default=SERVICE_SKELETON,
    help="A skeleton repository url that this command will utilize during this creation.",
)
@click.option(
    "--skeleton-branch",
    default=SKELETON_BRANCH,
    help="The branch or tag to use from the skeleton repository.",
)
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
    "--skip-cleanup",
    is_flag=True,
    default=False,
    help="If set, it will skip deleting the gernerated code after the command is finished.",
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
def generate(
    organization: str,
    name: str,
    skeleton_url: str,
    skeleton_branch: str,
    service_branch: str,
    skip_git: bool,
    skip_cleanup: bool,
    dry_run: bool,
):
    """Dynamically gneerates terragrunt files based off a service."""

    if dry_run:
        click.secho("Performing a dry run, nothing will be created", fg="yellow")

    service_path = f"{os.getcwd()}/{name}-singleRun"

    g = get_github_instance()
    repo = g.get_repo(f"{organization}/{name}")

    skeleton_repo = clone_repository(
        repository_url=skeleton_url, target=f"{name}-singleRun", branch=skeleton_branch
    )

    if not skip_git:
        service_repo = clone_repository(
            repository_url=repo.clone_url, target=f"{name}", branch=service_branch
        )

    with open(f"{os.getcwd()}/{name}", "r") as f:
        input_data = json.load(f)

    # Creating directories and copying properties files
    create_directories(service_path, input_data["platform"])
    copy_properties_files(service_path, input_data["platform"])

    # Placing Jinja templates
    template_paths, jinja_paths = list_jinja_templates(
        service_path / Path(".launch/jinja2")
    )
    copy_and_render_templates(
        base_dir=service_path,
        template_paths=template_paths,
        modified_paths=jinja_paths,
        context_data={"data": {"config": input_data}},
    )

    if not skip_cleanup:
        shutil.rmtree(f"{os.getcwd()}/{name}-singleRun")
