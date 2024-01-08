import pytest
import os
from unittest.mock import patch, MagicMock
from launch.pipeline.common.functions import copy_files_and_dirs


# Test for the case where is_infrastructure is True
def test_copy_files_for_infrastructure():
    path, repo_name, override = '/path', 'repo', {'infrastructure_dir': 'infra', 'properties_suffix': 'properties'}
    with patch('os.path.exists') as mock_exists, \
         patch('os.makedirs') as mock_makedirs, \
         patch('os.listdir') as mock_listdir, \
         patch('shutil.copy2') as mock_copy2:
        
        mock_exists.side_effect = lambda p: p.endswith('infra') and 'repo-properties' in p
        mock_listdir.return_value = ['file1', 'file2']
        source = f"{path}/{repo_name}-properties/infra"
        destination = f"{path}/{repo_name}/infra"

        copy_files_and_dirs(True, repo_name, path, None, override)

        mock_exists.assert_any_call(source)
        mock_makedirs.assert_called_with(destination)
        mock_copy2.assert_any_call(os.path.join(source, 'file1'), os.path.join(destination, 'file1'))
        mock_copy2.assert_any_call(os.path.join(source, 'file2'), os.path.join(destination, 'file2'))


# Test for the case where is_infrastructure is False
def test_copy_files_for_non_infrastructure():
    path, repo_name, target_env, override = '/path', 'repo', 'dev', {'environment_dir': 'env', 'properties_suffix': 'props'}
    with patch('os.path.exists') as mock_exists, \
         patch('os.makedirs') as mock_makedirs, \
         patch('os.listdir') as mock_listdir, \
         patch('shutil.copy2') as mock_copy2:

        # Adjusted to correctly simulate the file system state
        mock_exists.side_effect = lambda p: True if f"{repo_name}-{override['properties_suffix']}" in p else False
        mock_listdir.return_value = ['file1', 'file2']
        source = f"{path}/{repo_name}-{override['properties_suffix']}/env/dev"
        destination = f"{path}/{repo_name}/env/dev"

        copy_files_and_dirs(False, repo_name, path, target_env, override)

        mock_exists.assert_any_call(source)  # Changed to assert_any_call
        mock_makedirs.assert_called_with(destination)
        mock_copy2.assert_any_call(os.path.join(source, 'file1'), os.path.join(destination, 'file1'))
        mock_copy2.assert_any_call(os.path.join(source, 'file2'), os.path.join(destination, 'file2'))


# Test handling non-existent source directories
def test_handle_non_existent_source_dir():
    with patch('os.path.exists', return_value=False), \
         pytest.raises(RuntimeError) as excinfo:
        copy_files_and_dirs(True, 'repo', '/path', None, {'infrastructure_dir': 'infra', 'properties_suffix': '-props'})
    assert "Source directory not found" in str(excinfo.value)


# Test creation of destination directories
def test_create_destination_dir():
    path, repo_name, override = '/path', 'repo', {'infrastructure_dir': 'infra', 'properties_suffix': 'properties'}
    with patch('os.path.exists', side_effect=lambda p: 'repo-properties' in p), \
         patch('os.makedirs') as mock_makedirs, \
         patch('os.listdir', return_value=[]):
        copy_files_and_dirs(True, repo_name, path, None, override)
        destination = f"{path}/{repo_name}/infra"
        mock_makedirs.assert_called_with(destination)


# Test error handling during copy
def test_error_handling_during_copy():
    path, repo_name, override = '/path', 'repo', {'infrastructure_dir': 'infra', 'properties_suffix': '-props'}
    with patch('os.path.exists', return_value=True), \
         patch('os.makedirs'), \
         patch('os.listdir', return_value=['file1']), \
         patch('shutil.copy2', side_effect=Exception("Copy failed")), \
         pytest.raises(RuntimeError) as excinfo:
        copy_files_and_dirs(True, repo_name, path, None, override)
    assert "An error occurred: Copy failed" in str(excinfo.value)
