import pathlib
import subprocess
from test.unit.automation.helm.fixtures import isolated_helm_chart_with_dependencies

import pytest

from src.launch.automation.helm.functions import (
    add_dependency_repositories,
    extract_dependencies_from_chart,
    resolve_dependencies,
    resolve_next_layer_dependencies,
)


def test_extract_dependencies(isolated_helm_chart_with_dependencies):
    extracted_dependencies = extract_dependencies_from_chart(
        isolated_helm_chart_with_dependencies
    )
    assert len(extracted_dependencies) == 1
    assert extracted_dependencies[0]["name"] == "helm-library"
    assert extracted_dependencies[0]["version"] == "^2.0.0"
    assert extracted_dependencies[0]["repository"] == "file://../../charts/helm-library"


def test_resolve_dependencies_raises_error_if_no_chart_yaml(tmp_path):
    with pytest.raises(FileNotFoundError):
        resolve_dependencies(helm_directory=tmp_path)


def test_add_dependency_repositories(mocker):
    mocker.patch("subprocess.call")
    dependencies = [
        {
            "name": "foo",
            "version": "1.0.0",
            "repository": "https://foo.com/helm-repo/charts/",
        }
    ]
    add_dependency_repositories(dependencies)
    subprocess.call.assert_called_once_with(
        ["helm", "repo", "add", "foo", "https://foo.com/helm-repo/charts/"]
    )


def test_resolve_next_layer_dependencies(mocker):
    # Mock the necessary functions and objects
    dependencies = [
        {"name": "dependency1", "version": "1.0.0"},
        {"name": "dependency2", "version": "2.0.0"},
    ]
    helm_directory = pathlib.Path("/path/to/helm/directory")
    discover_files_mock = mocker.patch(
        "src.launch.automation.helm.functions.discover_files"
    )
    unpack_archive_mock = mocker.patch(
        "src.launch.automation.helm.functions.unpack_archive"
    )
    resolve_dependencies_mock = mocker.patch(
        "src.launch.automation.helm.functions.resolve_dependencies"
    )

    # Mock the return values of the mocked functions
    discover_files_mock.return_value = [
        "/path/to/dependency1_archive.tar.gz",
        "/path/to/dependency2_archive.tar.gz",
    ]

    # Call the function under test
    resolve_next_layer_dependencies(dependencies, helm_directory)

    # Assert the expected function calls
    discover_files_mock.assert_has_calls(
        [
            mocker.call(
                helm_directory.joinpath("charts"), filename_partial="dependency1"
            ),
            mocker.call(
                helm_directory.joinpath("charts"), filename_partial="dependency2"
            ),
        ]
    )
    unpack_archive_mock.assert_has_calls(
        [
            mocker.call(
                "/path/to/dependency1_archive.tar.gz", helm_directory.joinpath("charts")
            ),
            mocker.call(
                "/path/to/dependency2_archive.tar.gz", helm_directory.joinpath("charts")
            ),
        ]
    )
    resolve_dependencies_mock.assert_has_calls(
        [
            mocker.call(helm_directory.joinpath("charts/dependency1")),
            mocker.call(helm_directory.joinpath("charts/dependency2")),
        ]
    )
