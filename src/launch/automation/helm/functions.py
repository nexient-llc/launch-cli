import logging
import pathlib
import subprocess

from launch.automation.common.functions import discover_files, load_yaml, unpack_archive

logger = logging.getLogger(__name__)


def resolve_dependencies(helm_directory: pathlib.Path) -> None:
    # Entrypoint for CLI logic
    top_level_chart = helm_directory.joinpath("Chart.yaml")

    if not top_level_chart.exists():
        raise FileNotFoundError(f"No Chart.yaml found in {helm_directory}")

    dependencies = extract_dependencies_from_chart(chart_file=top_level_chart)
    for dependency in dependencies:
        # Your looping / recursion logic here
        # discover_files(...), unpack_archive(...), etc.
        # subprocess.call(["helm", "dep", "build", "."])
        ...


def extract_dependencies_from_chart(chart_file: pathlib.Path) -> list[dict[str, str]]:
    """Loads a Chart file and returns the contents of the 'dependencies' section.

    Args:
        chart_file (pathlib.Path): Path to a Helm Chart.yaml

    Returns:
        list[dict[str, str]]: A list of dependency objects, or an empty list if there are no dependencies.
    """
    yaml_contents = load_yaml(yaml_file=chart_file)
    dependencies = yaml_contents.get("dependencies", [])
    logger.debug(f"Loaded {len(dependencies)} dependencies from chart at {chart_file}")
    return dependencies
