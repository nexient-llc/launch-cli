import pytest
import subprocess

from unittest.mock import patch, MagicMock
from launch.pipeline.terragrunt.functions import *


@pytest.fixture(scope="function")

@patch('functions.subprocess.run')
def test_terragrunt_apply_run_all(mock_run):
    mock_run.return_value = MagicMock()
    terragrunt_apply(file=None, run_all=True)
    mock_run.assert_called_once_with(['terragrunt', 'run_all', 'apply', '-auto-approve'], check=True)

@patch('functions.subprocess.run')
def test_terragrunt_apply_no_run_all(mock_run):
    mock_run.return_value = MagicMock()
    terragrunt_apply(file=None, run_all=False)
    mock_run.assert_called_once_with(['terragrunt', 'apply', '-auto-approve'], check=True)

@patch('functions.subprocess.run')
def test_terragrunt_apply_with_file(mock_run):
    mock_run.return_value = MagicMock()
    terragrunt_apply(file='vars.tfvars', run_all=False)
    mock_run.assert_called_once_with(['terragrunt', 'apply', '-auto-approve', '-var-file', 'vars.tfvars'], check=True)

@patch('functions.subprocess.run')
def test_terragrunt_apply_exception(mock_run):
    mock_run.side_effect = subprocess.CalledProcessError(1, 'cmd')
    with pytest.raises(RuntimeError):
        terragrunt_apply()
