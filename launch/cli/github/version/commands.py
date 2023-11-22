import pathlib

import click

from launch.local_repo.branch import get_current_branch_name
from launch.local_repo.predict import InvalidBranchNameException, predict_version
from launch.local_repo.tags import read_semantic_tags


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
    """Creates a webhook for a single repository."""

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
    help="Predict next version of the repository located at this path. Can be relative or absolute, defaults to the current directory.",
)
def apply(repo_path: pathlib.Path):
    """Creates a webhook for a single repository."""
    raise NotImplementedError(f"would be applying version for repo at {repo_path}")
