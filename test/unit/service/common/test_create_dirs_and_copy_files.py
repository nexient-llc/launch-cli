from unittest.mock import patch, MagicMock, call
import pytest
from launch.service.common import create_dirs_and_copy_files

# Test copying a file when it exists
@patch('launch.service.common.os.path.exists', MagicMock(return_value=True))
@patch('launch.service.common.os.makedirs')
@patch('launch.service.common.shutil.copy')
@patch('launch.service.common.logger.info')
def test_copy_file_exists(mock_logger, mock_copy, mock_makedirs):
    base_path = '/base/path'
    nested_dict = {
        'properties_file': '/path/to/terraform.tfvars'
    }

    create_dirs_and_copy_files(base_path, nested_dict)

    mock_copy.assert_called_once_with('/path/to/terraform.tfvars', '/base/path/terraform.tfvars')
    mock_logger.assert_called_once_with('Copied /path/to/terraform.tfvars to /base/path/terraform.tfvars')
    mock_makedirs.assert_not_called()

# Test exception for non-existent file
@patch('launch.service.common.os.path.exists', MagicMock(return_value=False))
def test_copy_file_not_found():
    base_path = '/base/path'
    nested_dict = {
        'properties_file': '/path/to/nonexistent.tfvars'
    }

    with pytest.raises(Exception) as excinfo:
        create_dirs_and_copy_files(base_path, nested_dict)

    assert "File not found: /path/to/nonexistent.tfvars" in str(excinfo.value)

# Test creating directories for nested dictionaries
@patch('launch.service.common.os.path.exists', MagicMock(side_effect=lambda x: x == '/path/to/terraform.tfvars'))
@patch('launch.service.common.os.makedirs')
@patch('launch.service.common.shutil.copy')
@patch('launch.service.common.logger.info')
def test_create_nested_directories(mock_logger, mock_copy, mock_makedirs):
    base_path = '/base/path'
    nested_dict = {
        'dir1': {
            'properties_file': '/path/to/terraform.tfvars'
        },
        'dir2': {}
    }

    create_dirs_and_copy_files(base_path, nested_dict)

    mock_copy.assert_called_once_with('/path/to/terraform.tfvars', '/base/path/dir1/terraform.tfvars')
    mock_logger.assert_called_once_with('Copied /path/to/terraform.tfvars to /base/path/dir1/terraform.tfvars')
    mock_makedirs.assert_has_calls([
        call('/base/path/dir1'),
        call('/base/path/dir2')
    ], any_order=True)