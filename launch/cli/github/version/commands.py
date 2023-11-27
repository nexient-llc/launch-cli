import pathlib

import click

from launch.local_repo.branch import get_current_branch_name
from launch.local_repo.predict import predict_version
from launch.local_repo.tags import (
    create_version_tag,
    push_version_tag,
    read_semantic_tags,
)


@click.command()
@click.option(
    "--repo-path",
    type=click.Path(
        exists=True,
        file_okay=False,
        dir_okay=True,
        readable=True,
        resolve_path=True,
        path_type=pathlib.Path,
    ),
    default=".",
    help="Predict next version of the repository located at this path. Can be relative or absolute, defaults to the current directory.",
)
def predict(repo_path: pathlib.Path):
    """Predicts the next semantic version for a repository."""

    try:
        active_branch = get_current_branch_name(repo_path=repo_path)
        predicted_version = predict_version(
            existing_tags=read_semantic_tags(repo_path=repo_path),
            branch_name=active_branch,
        )
        print(predicted_version)
    except Exception as e:
        click.secho(
            f"Failed to predict next version for repository at {repo_path}: {e}",
            fg="red",
        )
        raise click.Abort()


@click.command()
@click.option(
    "--repo-path",
    type=click.Path(
        exists=True,
        file_okay=False,
        dir_okay=True,
        readable=True,
        resolve_path=True,
        path_type=pathlib.Path,
    ),
    default=".",
    help="Increment version of the repository located at this path. Can be relative or absolute, defaults to the current directory.",
)
@click.option(
    "--source-branch",
    type=click.STRING,
    help="Name of the branch that should be used to predict the next semantic version.",
)
def apply(repo_path: pathlib.Path, source_branch: str):
    """Predicts the next semantic version for a repository based on the provided source branch, then creates and pushes a tag."""
    # Safeguard to ensure that we can't accidentally bump a version if the branch is being merged against anything but main.
    active_branch = get_current_branch_name(repo_path=repo_path)
    if not active_branch == "main":
        click.secho(
            f"Failed to apply next version for repository at {repo_path}: repo is not on main branch!",
            fg="red",
        )
        raise click.Abort()

    try:
        predicted_version = predict_version(
            existing_tags=read_semantic_tags(repo_path=repo_path),
            branch_name=source_branch,
        )
    except Exception as e:
        click.secho(
            f"Failed to apply next version for repository at {repo_path} during prediction: {e}",
            fg="red",
        )
        raise click.Abort()

    try:
        new_tag = create_version_tag(repo_path=repo_path, version=predicted_version)
        push_version_tag(repo_path=repo_path, tag=new_tag)
        click.echo(f"Version is now {predicted_version}")
    except Exception as e:
        click.secho(
            f"Failed to apply next version for repository at {repo_path} during tagging: {e}",
            fg="red",
        )
        raise click.Abort()
