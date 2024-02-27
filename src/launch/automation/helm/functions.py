import logging
import pathlib
import subprocess

from launch.automation.common.functions import discover_files, load_yaml, unpack_archive

logger = logging.getLogger(__name__)


def resolve_dependencies(helm_directory: pathlib.Path) -> None:
    """Recursive function to resolve Helm dependencies based on Chart.yaml file in provided path.

    Args:
        helm_directory (pathlib.Path): Directory containing a Chart.yaml file.

    Raises:
        FileNotFoundError: If no Chart.yaml is found in the provided directory.
    """
    top_level_chart = helm_directory.joinpath("Chart.yaml")

    if not top_level_chart.exists():
        raise FileNotFoundError(f"No Chart.yaml found in {helm_directory}")

    dependencies = extract_dependencies_from_chart(chart_file=top_level_chart)
    add_dependency_repositories(dependencies)

    subprocess.call(["helm", "dep", "build", "."], cwd=helm_directory)

    resolve_next_layer_dependencies(dependencies, helm_directory)


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


def add_dependency_repositories(dependencies: list[dict[str, str]]) -> None:
    """Adds Helm repositories for each dependency in the provided list.

    Args:
        dependencies (list[dict[str, str]]): A list of dependency objects.
    """
    for dependency in dependencies:
        if dependency["repository"].startswith("file://"):
            # Local dependency, no need to fetch
            continue
        else:
            subprocess.call(
                ["helm", "repo", "add", dependency["name"], dependency["repository"]]
            )


def resolve_next_layer_dependencies(
    dependencies: list[dict[str, str]], helm_directory: pathlib.Path
) -> None:
    """Inspect any dependencies of the provided dependencies and resolve them.

    Args:
        dependencies (list[dict[str, str]]): A list of dependency objects.
        helm_directory (pathlib.Path): Directory containing a Chart.yaml file.
    """
    for dependency in dependencies:
        # Discover the dependency archives -- there should be one for each version, but only ever one version included as a dependency.
        dependency_archives = discover_files(
            helm_directory.joinpath("charts"), filename_partial=dependency["name"]
        )
        for dependency_archive in dependency_archives:
            unpack_archive(dependency_archive, helm_directory.joinpath("charts"))
            resolve_dependencies(
                helm_directory.joinpath(f"charts/{dependency['name']}")
            )
