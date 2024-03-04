import logging
import pathlib

import click

from launch.automation.helm.functions import (
    resolve_dependencies as resolve_helm_dependencies,
)

logger = logging.getLogger(__name__)


@click.command()
@click.option(
    "--path",
    default=pathlib.Path.cwd(),
    type=click.Path(
        exists=True,
        file_okay=False,
        dir_okay=True,
        resolve_path=True,
        path_type=pathlib.Path,
    ),
    help="Path to a folder containing your Chart.yaml. Defaults to the current working directory.",
)
def resolve_dependencies(path: pathlib.Path):
    """Resolves nested dependencies for a Helm chart."""
    try:
        logger.info(f"Resolving Helm dependencies in {path}.")
        resolve_helm_dependencies(helm_directory=path, global_dependencies={})
    except Exception as e:
        logger.exception(
            f"A failure occurred while resolving Helm dependencies. Error: {e}"
        )
