import shutil
import click
import logging
import json
import os
import re
import subprocess
from typing import IO, Any
from jinja2 import Environment, FileSystemLoader
from launch.github.auth import get_github_instance
from launch.github.repo import create_repository, clone_repository
from launch.cli.github.access.commands import set_default
from launch.service.common import create_dirs_and_copy_files, traverse_and_render

from launch import GITHUB_ORG_NAME, SERVICE_SKELETON, SKELETON_BRANCH, MAIN_BRANCH, INIT_BRANCH

logger = logging.getLogger(__name__)

@click.command()
@click.option(
    "--organization",
    default=GITHUB_ORG_NAME,
    help="GitHub organization containing your repository. Defaults to the nexient-llc organization.",
)
@click.option(
    "--name", 
    required=True, 
    help="(Required) Name of the service to  be created."
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
    type=click.File('r'),
    help="(Required) Inputs to be used with the skeleton during creation.",
)
@click.option(
    "--dry-run",
    is_flag=True,
    default=False,
    help="Perform a dry run that reports on what it would do, but does not create webhooks.",
)
@click.pass_context
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
        click.secho(
            "Performing a dry run, nothing will be created", fg="yellow"
        )
        
    service_path =f"{os.getcwd()}/{name}"
    
    g = get_github_instance()
    
    skeleton_repo = clone_repository(
        repository_url=skeleton_url,
        target=name,
        branch=skeleton_branch
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
    skeleton_repo.delete_remote('origin')
    origin = skeleton_repo.create_remote('origin', service_repo.clone_url)
    origin.push(refspec='{}:{}'.format(skeleton_branch, main_branch))
    context.invoke(set_default, organization=organization, repository_name=name, dry_run=dry_run)

    # PyGithub doesn't have good support with interacting with local repos
    subprocess.run(["git", "pull", "origin", main_branch], cwd=service_path)
    subprocess.run(["git", "checkout", "-b", init_branch], cwd=service_path)

    service_config = json.load(in_file)
    create_dirs_and_copy_files(
        base_path=f"{service_path}/platform", 
        nested_dict=service_config['platform']
    )

    # Jinja2 creation
    with open(f"{service_path}/.launch/jinja2/file_structure.json", 'r') as file:
        j2_file_structure = json.load(file)

    template_dir = f"{service_path}/.launch/jinja2/{service_config['provider']}/"
    j2_env = Environment(loader=FileSystemLoader(template_dir))

    traverse_and_render(
        service_path, 
        j2_file_structure,
        service_config,
        j2_env
    )

    # Remove the .launch directory
    shutil.rmtree(f"{service_path}/.launch")

    # PyGithub doesn't have good support with interacting with local repos
    subprocess.run(["git", "add", "."], cwd=service_path)
    subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=service_path)
    subprocess.run(["git", "push", "--set-upstream", "origin", init_branch], cwd=service_path)