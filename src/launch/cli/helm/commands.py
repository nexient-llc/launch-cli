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
    help="Path to a folder containing your Chart.yaml. Defaults to the current working directory.",
)
def resolve_dependencies(path: pathlib.Path):
    """Resolves nested dependencies for a Helm chart."""
    try:
        resolve_helm_dependencies(helm_directory=path)
    except Exception as e:
        logger.exception("A failure occurred while resolving Helm dependencies.")
