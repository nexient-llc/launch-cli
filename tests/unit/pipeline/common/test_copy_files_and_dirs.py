import pytest

from unittest.mock import patch
from launch.pipeline.common.functions import *


def test_source_directory_not_exists(mocker):
    mocker.patch('os.path.exists', return_value=False)
    with pytest.raises(RuntimeError, match="Source directory not found"):
        copy_files_and_dirs("nonexistent/source", "destination")

def test_create_destination_directory(mocker):
    mocker.patch('os.path.exists', side_effect=lambda x: x == "source")
    mock_makedirs = mocker.patch('os.makedirs')
    mock_listdir = mocker.patch('os.listdir', return_value=[])

    copy_files_and_dirs("source", "new/destination")

    mock_makedirs.assert_called_once_with("new/destination")
    mock_listdir.assert_called_once_with("source")

def test_copy_files(mocker):
    mocker.patch('os.path.exists', return_value=True)
    mocker.patch('os.listdir', return_value=["file1.txt", "file2.txt"])
    mocker.patch('os.path.join', side_effect=lambda a, b: f"{a}/{b}")
    mocker.patch('os.path.isdir', return_value=False)
    mock_copy2 = mocker.patch('shutil.copy2')

    copy_files_and_dirs("source", "destination")

    assert mock_copy2.call_args_list == [
        mocker.call("source/file1.txt", "destination/file1.txt"),
        mocker.call("source/file2.txt", "destination/file2.txt"),
    ]

def test_recursive_directory_copy(mocker):
    mocker.patch('os.path.exists', return_value=True)
    mocker.patch('os.listdir', return_value=["dir1"])
    mocker.patch('os.path.isdir', side_effect=lambda x: x == "source/dir1")
    mocker.patch('os.makedirs', side_effect=OSError("Directory exists"))

    with patch('launch.pipeline.common.functions.copy_files_and_dirs') as mock_recursive_call: 
        copy_files_and_dirs("source", "destination")
        mock_recursive_call.assert_called_once_with("source/dir1", "destination/dir1")


def test_exception_during_file_copy(mocker):
    mocker.patch('os.path.exists', return_value=True)
    mocker.patch('os.listdir', return_value=["file1.txt"])
    mocker.patch('os.path.join', side_effect=lambda a, b: f"{a}/{b}")
    mocker.patch('os.path.isdir', return_value=False)
    mocker.patch('shutil.copy2', side_effect=Exception("Copy failed"))

    with pytest.raises(RuntimeError, match="An error occurred"):
        copy_files_and_dirs("source", "destination")
