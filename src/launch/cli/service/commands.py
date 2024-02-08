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
from launch.github.repo import clone_repository, create_repository
from launch.service.common import (
    copy_and_render_templates,
    copy_properties_files,
    create_directories,
    list_jinja_templates,
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
    skeleton_url: str,
    skeleton_branch: str,
    public: bool,
    visibility: str,
    main_branch: str,
    init_branch: str,
    in_file: IO[Any],
    dry_run: bool,
):
    """Creates a new service."""

    if dry_run:
        click.secho("Performing a dry run, nothing will be created", fg="yellow")

    service_path = f"{os.getcwd()}/{name}"
    input_data = json.load(in_file)

    g = get_github_instance()

    skeleton_repo = clone_repository(
        repository_url=skeleton_url, target=name, branch=skeleton_branch
    )

    service_repo = create_repository(
        g=g,
        organization=organization,
        name=name,
        description=description,
        public=public,
        visibility=visibility,
    )

    # Since we copied the skeleton repo, we need to update the origin
    skeleton_repo.delete_remote("origin")
    origin = skeleton_repo.create_remote("origin", service_repo.clone_url)
    origin.push(refspec=f"{skeleton_branch}:{main_branch}")
    context.invoke(
        set_default, organization=organization, repository_name=name, dry_run=dry_run
    )

    # PyGithub doesn't have good support with interacting with local repos
    subprocess.run(["git", "pull", "origin", main_branch], cwd=service_path)
    subprocess.run(["git", "checkout", "-b", init_branch], cwd=service_path)

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

    # Remove the .launch directory
    shutil.rmtree(f"{service_path}/.launch")
    # Append .launch to .gitignore
    # TODO: Convert to pathlib
    with open(f"{service_path}/.gitignore", "a") as file:
        file.write("# launch-cli tool\n.launch/\n")

    # PyGithub doesn't have good support with interacting with local repos
    subprocess.run(["git", "add", "."], cwd=service_path)
    subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=service_path)
    subprocess.run(
        ["git", "push", "--set-upstream", "origin", init_branch], cwd=service_path
    )
