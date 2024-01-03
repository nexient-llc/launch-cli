import pytest
import subprocess

from unittest.mock import patch, MagicMock
from launch.pipeline.terragrunt.functions import *


@pytest.fixture(scope="function")

@patch('functions.subprocess.run')
def test_terragrunt_plan_run_all(mock_run):
    mock_run.return_value = MagicMock()
    terragrunt_plan(file=None, run_all=True)
    mock_run.assert_called_once_with(['terragrunt', 'run_all', 'plan'], check=True)

@patch('functions.subprocess.run')
def test_terragrunt_plan_no_run_all(mock_run):
    mock_run.return_value = MagicMock()
    terragrunt_plan(file=None, run_all=False)
    mock_run.assert_called_once_with(['terragrunt', 'plan'], check=True)

@patch('functions.subprocess.run')
def test_terragrunt_plan_with_file(mock_run):
    mock_run.return_value = MagicMock()
    terragrunt_plan(file='plan.out', run_all=False)
    mock_run.assert_called_once_with(['terragrunt', 'plan', '-out', 'plan.out'], check=True)

@patch('functions.subprocess.run')
def test_terragrunt_plan_exception(mock_run):
    mock_run.side_effect = subprocess.CalledProcessError(1, 'cmd')
    with pytest.raises(RuntimeError):
        terragrunt_plan()
