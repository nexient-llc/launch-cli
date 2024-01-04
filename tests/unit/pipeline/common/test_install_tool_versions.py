import pytest

from unittest.mock import mock_open
from launch.pipeline.common.functions import *


@pytest.fixture(scope="function")

def test_install_tool_versions_success(mocker):
    # Mock the open function and the subprocess.run call
    mocker.patch("builtins.open", mock_open(read_data="tool1\n tool2"))
    mock_run = mocker.patch("subprocess.run")

    install_tool_versions("fake_file")

    # Check if subprocess.run was called correctly
    mock_run.assert_has_calls([
        mocker.call(['asdf', 'plugin', 'add', 'tool1'], check=True),
        mocker.call(['asdf', 'plugin', 'add', 'tool2'], check=True),
        mocker.call(['asdf', 'install'], check=True),
    ])


def test_install_tool_versions_file_read_exception(mocker):
    # Mock open to raise an exception
    mocker.patch("builtins.open", side_effect=IOError("File not found"))

    with pytest.raises(RuntimeError, match="An error occurred with asdf install"):
        install_tool_versions("fake_file")


def test_install_tool_versions_subprocess_exception(mocker):
    # Mock the open function and the subprocess.run call
    mocker.patch("builtins.open", mock_open(read_data="tool1\n tool2"))
    mocker.patch("subprocess.run", side_effect=subprocess.CalledProcessError(1, ['asdf']))

    with pytest.raises(RuntimeError, match="An error occurred with asdf install"):
        install_tool_versions("fake_file")