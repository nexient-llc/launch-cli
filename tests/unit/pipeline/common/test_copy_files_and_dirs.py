import pytest

from unittest.mock import patch
import launch.pipeline.common.functions as common


@pytest.fixture(scope="function")

# copy_files_and_dirs
@patch('functions.os.path.exists', return_value=True)
@patch('functions.os.listdir', return_value=['file'])
@patch('functions.os.path.isdir', return_value=False)
@patch('functions.shutil.copy2')
def test_copy_files_and_dirs_file(mock_copy2, mock_isdir, mock_listdir, mock_exists):
    common.copy_files_and_dirs('source_dir', 'destination_dir')
    mock_copy2.assert_called_once_with('source_dir/file', 'destination_dir/file')

@patch('functions.os.path.exists', return_value=True)
@patch('functions.os.listdir', return_value=['dir'])
@patch('functions.os.path.isdir', return_value=True)
@patch('functions.shutil.copytree')
def test_copy_files_and_dirs_dir_no_exist(mock_copytree, mock_isdir, mock_listdir, mock_exists):
    common.copy_files_and_dirs('source_dir', 'destination_dir')
    mock_copytree.assert_called_once_with('source_dir/dir', 'destination_dir/dir')

@patch('functions.os.path.exists', return_value=True)
@patch('functions.os.listdir', return_value=['dir'])
@patch('functions.os.path.isdir', side_effect=[True, False])
@patch('functions.shutil.copytree')
@patch('functions.shutil.copy2')
def test_copy_files_and_dirs_dir_exist(mock_copy2, mock_copytree, mock_isdir, mock_listdir, mock_exists):
    common.copy_files_and_dirs('source_dir', 'destination_dir')
    mock_copy2.assert_called_once_with('source_dir/dir', 'destination_dir/dir')

@patch('functions.os.path.exists', return_value=False)
def test_copy_files_and_dirs_no_source(mock_exists):
    common.copy_files_and_dirs('source_dir', 'destination_dir')
    mock_exists.assert_called_once_with('source_dir')