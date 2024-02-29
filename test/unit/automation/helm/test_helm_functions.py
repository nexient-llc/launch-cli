import pathlib
import subprocess
from test.unit.automation.helm.fixtures import (
    chartfile_local_deps,
    chartfile_mixed_deps,
    chartfile_no_deps,
    chartfile_remote_deps,
    conflict_global_dependencies,
    empty_dependencies,
    empty_global_dependencies,
    eq_global_dependencies,
    helm_directory,
    local_dependencies,
    mixed_dependencies,
    remote_dependencies,
    simple_chart_no_deps,
    top_level_chart,
)
from typing import Generator
from unittest import mock

import pytest

from src.launch.automation.helm.functions import (
    add_dependency_repositories,
    extract_dependencies_from_chart,
    resolve_dependencies,
    resolve_next_layer_dependencies,
)


def helm_add_repo_call(dependencies: list[dict[str, str]]):
    helm_add_repo_calls = []
    for dep in dependencies:
        if not dep["repository"].startswith("file://"):
            this_call = mock.Mock()
            this_call.call_args = mock.call(
                ["helm", "repo", "add", dep["name"], dep["repository"]]
            )
            helm_add_repo_calls.append(this_call.call_args)
    return helm_add_repo_calls


def call_list_from_call_strings(call_strings: list[str]):
    call_list = []
    for call in call_strings:
        this_call = mock.Mock()
        this_call.call_args = mock.call(call)
        call_list.append(this_call.call_args)
    return call_list


def helm_dep_archives_from_dependencies(dependencies: list[dict[str, str]]):
    helm_dep_archives = []
    for dep in dependencies:
        helm_dep_archives.append(
            f"/mock/path/to/dependency/{dep['name']}-{dep['version']}.tgz"
        )
    return helm_dep_archives


def test_extract_dependencies_none(
    chartfile_no_deps,
):
    extracted_dependencies = extract_dependencies_from_chart(chartfile_no_deps)
    assert len(extracted_dependencies) == 0


def test_extract_dependencies_mixed(chartfile_mixed_deps, mixed_dependencies):
    extracted_dependencies = extract_dependencies_from_chart(chartfile_mixed_deps)
    assert len(extracted_dependencies) == len(mixed_dependencies)
    assert extracted_dependencies == mixed_dependencies


def test_resolve_dependencies_raises_error_if_no_chart_yaml(tmp_path):
    with pytest.raises(FileNotFoundError):
        resolve_dependencies(helm_directory=tmp_path, global_dependencies={})


def test_add_remote_dependency_repositories(mocker, remote_dependencies):
    mocker.patch("subprocess.call")
    dependencies = remote_dependencies
    helm_call = helm_add_repo_call(dependencies)
    add_dependency_repositories(dependencies)
    assert subprocess.call.mock_calls == helm_call


def test_add_mixed_dependency_repositories(mocker, mixed_dependencies):
    mocker.patch("subprocess.call")
    dependencies = mixed_dependencies
    helm_call = helm_add_repo_call(dependencies)
    add_dependency_repositories(dependencies)
    assert subprocess.call.mock_calls == helm_call


def test_add_dependency_repositories_local_dependency(mocker, local_dependencies):
    mocker.patch("subprocess.call")
    dependencies = local_dependencies
    add_dependency_repositories(dependencies)
    subprocess.call.assert_not_called()


def test_resolve_next_layer_dependencies_empty_dependencies(
    mocker, empty_dependencies, helm_directory, empty_global_dependencies
):
    mock_discover_files = mocker.patch(
        "src.launch.automation.helm.functions.discover_files"
    )
    mock_logger_debug = mocker.patch(
        "src.launch.automation.helm.functions.logger.debug"
    )
    global_dependencies = empty_global_dependencies
    dependencies = empty_dependencies
    mock_discover_files.return_value = helm_dep_archives_from_dependencies(dependencies)
    resolve_next_layer_dependencies(dependencies, helm_directory, global_dependencies)
    mock_logger_debug.assert_called_with(
        f"Inspecting {len(dependencies)} dependencies for further dependencies."
    )
    mock_discover_files.assert_not_called()


def test_resolve_next_layer_dependencies_mixed_dependencies(
    mocker, mixed_dependencies, helm_directory, empty_global_dependencies
):
    # Create our list of mock archive paths
    dependency_archives = helm_dep_archives_from_dependencies(mixed_dependencies)

    # Create our list of expected debug output strings
    dependency_archives_debug_call_strings = []
    debug_call_strings = []
    for dependency_archive in dependency_archives:
        dependency_archives_debug_call_strings.append(
            f"Unpacking {dependency_archive} to {helm_directory.joinpath('charts')}".strip()
        )
    debug_call_strings = [
        f"Inspecting {len(mixed_dependencies)} dependencies for further dependencies.",
        f"Found {len(mixed_dependencies)} archives.",
    ]
    debug_call_strings.extend(dependency_archives_debug_call_strings)
    debug_call_args_assertions = call_list_from_call_strings(debug_call_strings)

    # Create mock objects of the associated functions
    mock_resolve_dependencies = mocker.patch(
        "src.launch.automation.helm.functions.resolve_dependencies"
    )
    mock_discover_files = mocker.patch(
        "src.launch.automation.helm.functions.discover_files"
    )
    mock_logger_debug = mocker.patch(
        "src.launch.automation.helm.functions.logger.debug"
    )
    mock_unpack_archive = mocker.patch(
        "src.launch.automation.helm.functions.unpack_archive"
    )

    # Set up our test
    global_dependencies = empty_global_dependencies
    dependencies = mixed_dependencies
    mock_discover_files.return_value = dependency_archives
    mock_unpack_archive.return_value = True
    mock_resolve_dependencies.return_value = None

    # Call the function being tested
    resolve_next_layer_dependencies(dependencies, helm_directory, global_dependencies)
    # review outputs for expected results
    mock_logger_debug.assert_has_calls(debug_call_args_assertions)


def test_resolve_dependencies_empty_global_empty_deps(
    mocker, empty_dependencies, helm_directory, empty_global_dependencies
):
    dependencies = empty_dependencies
    global_dependencies = empty_global_dependencies
    debug_call_strings = [
        f"Looking for Chart.yaml in {helm_directory}",
        f"Found {len(dependencies)} dependencies in {helm_directory}",
    ]
    debug_call_args_assertions = call_list_from_call_strings(debug_call_strings)

    info_call_strings = []
    exception_call_strings = []
    for dep in dependencies:
        if dep["name"] not in global_dependencies:
            info_call_strings.append(
                f"Remembering dependency {dep['name']} with version {dep['version']}."
            )
        elif global_dependencies[dep["name"]] != dep["version"]:
            exception_call_strings.append(
                f"Dependency {dep['name']} has conflicting versions: "
                f"{global_dependencies[dep['name']]} and {dep['version']}. "
                "You must resolve this conflict before continuing."
            )
        else:
            info_call_strings.append(
                f"Dependency {dep['name']} already known with version {dep['version']}."
            )

    info_call_args_assertions = call_list_from_call_strings(info_call_strings)
    exception_call_args_assertions = call_list_from_call_strings(exception_call_strings)

    mock_chart_exists = mocker.patch("pathlib.Path.exists")
    mock_subprocess_call = mocker.patch("subprocess.call")
    mock_extract_dependencies_from_chart = mocker.patch(
        "src.launch.automation.helm.functions.extract_dependencies_from_chart"
    )
    mock_add_dependency_repositories = mocker.patch(
        "src.launch.automation.helm.functions.add_dependency_repositories"
    )
    mock_resolve_next_layer_dependencies = mocker.patch(
        "src.launch.automation.helm.functions.resolve_next_layer_dependencies"
    )
    mock_logger_info = mocker.patch("src.launch.automation.helm.functions.logger.info")
    mock_logger_debug = mocker.patch(
        "src.launch.automation.helm.functions.logger.debug"
    )
    mock_logger_exception = mocker.patch(
        "src.launch.automation.helm.functions.logger.exception"
    )
    top_level_chart = helm_directory.joinpath("Chart.yaml")

    mock_chart_exists.return_value = True
    mock_subprocess_call.return_value = True
    mock_resolve_next_layer_dependencies.return_value = None
    mock_add_dependency_repositories.return_value = None
    resolve_dependencies(helm_directory, empty_global_dependencies)
    mock_extract_dependencies_from_chart.assert_called_with(chart_file=top_level_chart)
    mock_logger_debug.assert_has_calls(debug_call_args_assertions)
    mock_logger_info.assert_has_calls(info_call_args_assertions)
    mock_logger_exception.assert_has_calls(exception_call_args_assertions)


def test_resolve_dependencies_empty_global_mixed_deps(
    mocker, mixed_dependencies, helm_directory, empty_global_dependencies
):
    dependencies = mixed_dependencies
    global_dependencies = empty_global_dependencies
    debug_call_strings = [
        f"Looking for Chart.yaml in {helm_directory}",
        f"Found {len(dependencies)} dependencies in {helm_directory}",
    ]
    debug_call_args_assertions = call_list_from_call_strings(debug_call_strings)

    info_call_strings = []
    exception_call_strings = []
    for dep in dependencies:
        if dep["name"] not in global_dependencies:
            info_call_strings.append(
                f"Remembering dependency {dep['name']} with version {dep['version']}."
            )
        elif global_dependencies[dep["name"]] != dep["version"]:
            exception_call_strings.append(
                f"Dependency {dep['name']} has conflicting versions: "
                f"{global_dependencies[dep['name']]} and {dep['version']}. "
                "You must resolve this conflict before continuing."
            )
        else:
            info_call_strings.append(
                f"Dependency {dep['name']} already known with version {dep['version']}."
            )

    info_call_args_assertions = call_list_from_call_strings(info_call_strings)
    exception_call_args_assertions = call_list_from_call_strings(exception_call_strings)

    mock_chart_exists = mocker.patch("pathlib.Path.exists")
    mock_subprocess_call = mocker.patch("subprocess.call")
    mock_extract_dependencies_from_chart = mocker.patch(
        "src.launch.automation.helm.functions.extract_dependencies_from_chart"
    )
    mock_add_dependency_repositories = mocker.patch(
        "src.launch.automation.helm.functions.add_dependency_repositories"
    )
    mock_resolve_next_layer_dependencies = mocker.patch(
        "src.launch.automation.helm.functions.resolve_next_layer_dependencies"
    )
    mock_logger_info = mocker.patch("src.launch.automation.helm.functions.logger.info")
    mock_logger_debug = mocker.patch(
        "src.launch.automation.helm.functions.logger.debug"
    )
    mock_logger_exception = mocker.patch(
        "src.launch.automation.helm.functions.logger.exception"
    )
    top_level_chart = helm_directory.joinpath("Chart.yaml")

    mock_extract_dependencies_from_chart.return_value = dependencies
    mock_chart_exists.return_value = True
    mock_subprocess_call.return_value = True
    mock_resolve_next_layer_dependencies.return_value = None
    mock_add_dependency_repositories.return_value = None

    resolve_dependencies(helm_directory, empty_global_dependencies)
    mock_extract_dependencies_from_chart.assert_called_with(chart_file=top_level_chart)
    mock_logger_debug.assert_has_calls(debug_call_args_assertions)
    mock_logger_info.assert_has_calls(info_call_args_assertions)
    mock_logger_exception.assert_has_calls(exception_call_args_assertions)


def test_resolve_dependencies_eq_global_mixed_deps(
    mocker, mixed_dependencies, helm_directory, eq_global_dependencies
):
    dependencies = mixed_dependencies
    global_dependencies = eq_global_dependencies
    debug_call_strings = [
        f"Looking for Chart.yaml in {helm_directory}",
        f"Found {len(dependencies)} dependencies in {helm_directory}",
    ]
    debug_call_args_assertions = call_list_from_call_strings(debug_call_strings)

    info_call_strings = []
    exception_call_strings = []
    for dep in dependencies:
        if dep["name"] not in global_dependencies:
            info_call_strings.append(
                f"Remembering dependency {dep['name']} with version {dep['version']}."
            )
        elif global_dependencies[dep["name"]] != dep["version"]:
            exception_call_strings.append(
                f"Dependency {dep['name']} has conflicting versions: "
                f"{global_dependencies[dep['name']]} and {dep['version']}. "
                "You must resolve this conflict before continuing."
            )
        else:
            info_call_strings.append(
                f"Dependency {dep['name']} already known with version {dep['version']}."
            )

    info_call_args_assertions = call_list_from_call_strings(info_call_strings)
    exception_call_args_assertions = call_list_from_call_strings(exception_call_strings)

    mock_chart_exists = mocker.patch("pathlib.Path.exists")
    mock_subprocess_call = mocker.patch("subprocess.call")
    mock_extract_dependencies_from_chart = mocker.patch(
        "src.launch.automation.helm.functions.extract_dependencies_from_chart"
    )
    mock_add_dependency_repositories = mocker.patch(
        "src.launch.automation.helm.functions.add_dependency_repositories"
    )
    mock_resolve_next_layer_dependencies = mocker.patch(
        "src.launch.automation.helm.functions.resolve_next_layer_dependencies"
    )
    mock_logger_info = mocker.patch("src.launch.automation.helm.functions.logger.info")
    mock_logger_debug = mocker.patch(
        "src.launch.automation.helm.functions.logger.debug"
    )
    mock_logger_exception = mocker.patch(
        "src.launch.automation.helm.functions.logger.exception"
    )
    top_level_chart = helm_directory.joinpath("Chart.yaml")

    mock_extract_dependencies_from_chart.return_value = dependencies
    mock_chart_exists.return_value = True
    mock_subprocess_call.return_value = True
    mock_resolve_next_layer_dependencies.return_value = None
    mock_add_dependency_repositories.return_value = None

    resolve_dependencies(helm_directory, global_dependencies)
    mock_extract_dependencies_from_chart.assert_called_with(chart_file=top_level_chart)
    mock_logger_debug.assert_has_calls(debug_call_args_assertions)
    mock_logger_info.assert_has_calls(info_call_args_assertions)
    mock_logger_exception.assert_has_calls(exception_call_args_assertions)


def test_resolve_dependencies_conflict_global_mixed_deps(
    mocker, mixed_dependencies, helm_directory, conflict_global_dependencies
):
    dependencies = mixed_dependencies
    global_dependencies = conflict_global_dependencies
    debug_call_strings = [
        f"Looking for Chart.yaml in {helm_directory}",
        f"Found {len(dependencies)} dependencies in {helm_directory}",
    ]
    debug_call_args_assertions = call_list_from_call_strings(debug_call_strings)

    info_call_strings = []
    exception_call_strings = []
    for dep in dependencies:
        if dep["name"] not in global_dependencies:
            info_call_strings.append(
                f"Remembering dependency {dep['name']} with version {dep['version']}."
            )
        elif global_dependencies[dep["name"]] != dep["version"]:
            exception_call_strings.append(
                f"Dependency {dep['name']} has conflicting versions: "
                f"{global_dependencies[dep['name']]} and {dep['version']}. "
                "You must resolve this conflict before continuing."
            )
        else:
            info_call_strings.append(
                f"Dependency {dep['name']} already known with version {dep['version']}."
            )

    info_call_args_assertions = call_list_from_call_strings(info_call_strings)
    exception_call_args_assertions = call_list_from_call_strings(exception_call_strings)

    mock_chart_exists = mocker.patch("pathlib.Path.exists")
    mock_subprocess_call = mocker.patch("subprocess.call")
    mock_exit = mocker.patch("sys.exit")
    mock_extract_dependencies_from_chart = mocker.patch(
        "src.launch.automation.helm.functions.extract_dependencies_from_chart"
    )
    mock_add_dependency_repositories = mocker.patch(
        "src.launch.automation.helm.functions.add_dependency_repositories"
    )
    mock_resolve_next_layer_dependencies = mocker.patch(
        "src.launch.automation.helm.functions.resolve_next_layer_dependencies"
    )
    mock_logger_info = mocker.patch("src.launch.automation.helm.functions.logger.info")
    mock_logger_debug = mocker.patch(
        "src.launch.automation.helm.functions.logger.debug"
    )
    mock_logger_exception = mocker.patch(
        "src.launch.automation.helm.functions.logger.exception"
    )
    top_level_chart = helm_directory.joinpath("Chart.yaml")

    mock_extract_dependencies_from_chart.return_value = dependencies
    mock_chart_exists.return_value = True
    mock_subprocess_call.return_value = True
    mock_resolve_next_layer_dependencies.return_value = None
    mock_add_dependency_repositories.return_value = None

    resolve_dependencies(helm_directory, global_dependencies)
    mock_extract_dependencies_from_chart.assert_called_with(chart_file=top_level_chart)
    mock_logger_debug.assert_has_calls(debug_call_args_assertions)
    mock_logger_info.assert_has_calls(info_call_args_assertions)
    mock_logger_exception.assert_has_calls(exception_call_args_assertions)
    mock_exit.assert_called_once_with(1)
