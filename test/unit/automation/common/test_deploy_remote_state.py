import subprocess
from unittest.mock import MagicMock, patch

import pytest

from launch.automation.common.functions import (
    deploy_remote_state,  # Adjust based on your module structure
)


def test_deploy_remote_state_success():
    mock_provider_config = {
        "az": {
            "name_prefix": "mockednp",
            "region": "mock-region",
        }
    }
    expected_run_list = [
        "make",
        "NAME_PREFIX=mockednp",
        "REGION=mock-region",
        "terragrunt/remote_state/azure",
    ]

    with patch("subprocess.run") as mock_run:
        deploy_remote_state(mock_provider_config)
        mock_run.assert_called_once_with(expected_run_list, check=True)


def test_deploy_remote_state_failure():
    provider_config = {"az": {"name_prefix": "np"}}
    with patch("subprocess.run") as mock_run, pytest.raises(RuntimeError) as exc_info:
        mock_run.side_effect = subprocess.CalledProcessError(1, "make")
        deploy_remote_state(provider_config)
        assert "An error occurred:" in str(exc_info.value)
