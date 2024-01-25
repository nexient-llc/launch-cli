import pytest
import subprocess
from unittest.mock import patch, MagicMock
from launch.automation.terragrunt.functions import terragrunt_destroy


@pytest.fixture(scope="function")

@patch('subprocess.run')
def test_terragrunt_destroy_run_all(mock_run):
    mock_run.return_value = MagicMock()
    terragrunt_destroy(file=None, run_all=True)
    mock_run.assert_called_once_with(['terragrunt', 'run_all', 'destroy', '-auto-approve'], check=True)


@patch('subprocess.run')
def test_terragrunt_destroy_no_run_all(mock_run):
    mock_run.return_value = MagicMock()
    terragrunt_destroy(file=None, run_all=False)
    mock_run.assert_called_once_with(['terragrunt', 'destroy', '-auto-approve'], check=True)


@patch('subprocess.run')
def test_terragrunt_destroy_with_file(mock_run):
    mock_run.return_value = MagicMock()
    terragrunt_destroy(file='vars.tfvars', run_all=False)
    mock_run.assert_called_once_with(['terragrunt', 'destroy', '-auto-approve', '-var-file', 'vars.tfvars'], check=True)


@patch('subprocess.run')
def test_terragrunt_destroy_exception(mock_run):
    mock_run.side_effect = subprocess.CalledProcessError(1, 'cmd')
    with pytest.raises(RuntimeError):
        terragrunt_destroy()
