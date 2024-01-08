import pytest
import subprocess
from unittest.mock import patch, MagicMock
from launch.pipeline.terragrunt.functions import terragrunt_init


@pytest.fixture(scope="function")

@patch('subprocess.run')
def test_terragrunt_init_run_all(mock_run):
    mock_run.return_value = MagicMock()
    terragrunt_init(run_all=True)
    mock_run.assert_called_once_with(['terragrunt', 'run_all', 'init', '--terragrunt-non-interactive'], check=True)


@patch('subprocess.run')
def test_terragrunt_init_no_run_all(mock_run):
    mock_run.return_value = MagicMock()
    terragrunt_init(run_all=False)
    mock_run.assert_called_once_with(['terragrunt', 'init', '--terragrunt-non-interactive'], check=True)


@patch('subprocess.run')
def test_terragrunt_init_exception(mock_run):
    mock_run.side_effect = subprocess.CalledProcessError(1, 'cmd')
    with pytest.raises(RuntimeError):
        terragrunt_init()
