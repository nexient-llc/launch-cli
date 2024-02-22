from pathlib import Path
from unittest.mock import MagicMock

import pytest

from launch.service.common import write_launch_config


@pytest.fixture
def mock_path(tmp_path):
    mock_path = MagicMock(spec=Path)
    mock_path.write_text = MagicMock(return_value=None)
    return mock_path


def test_write_launch_config_with_valid_data(mock_path):
    data = {"key": "value"}
    write_launch_config(data, mock_path)
    assert mock_path.write_text.called


def test_write_launch_config_with_empty_dict(mock_path):
    data = {}
    write_launch_config(data, mock_path)
    mock_path.write_text.assert_called()


def test_write_launch_config_with_valid_data(mock_path):
    data = {"key": "value"}
    write_launch_config(data, mock_path)
    mock_path.write_text.assert_called()


def test_write_launch_config_with_empty_dict(mock_path):
    data = {}
    write_launch_config(data, mock_path)
    mock_path.write_text.assert_called()
