import json
from pathlib import Path
from unittest.mock import patch

import pytest

from launch.automation.common.functions import traverse_with_callback
from launch.automation.provider.az.functions import callback_deploy_remote_state


@pytest.fixture
def fakedata():
    config_path = Path(__file__).parent / "data" / "fakedata.json"
    with config_path.open() as f:
        return json.load(f)


# Test cases
def test_simple_dict_callback_interaction(fakedata):
    with patch(
        "launch.automation.provider.az.functions.deploy_remote_state"
    ) as mock_deploy:
        fakedata["kwargs"]["current_path"] = Path(fakedata["kwargs"]["current_path"])
        traverse_with_callback(
            fakedata["simple_dict"], callback_deploy_remote_state, **fakedata["kwargs"]
        )
        mock_deploy.assert_called_once_with(
            uuid_value="1234-5678",
            naming_prefix="test-prefix",
            target_environment="production",
            region="us-east-1",
            instance="000",
            provider_config={"key": "value"},
        )


def test_nested_dict_callback_interaction(fakedata):
    with patch(
        "launch.automation.provider.az.functions.deploy_remote_state"
    ) as mock_deploy:
        fakedata["kwargs"]["current_path"] = Path(fakedata["kwargs"]["current_path"])
        traverse_with_callback(
            fakedata["nested_dict"], callback_deploy_remote_state, **fakedata["kwargs"]
        )
        mock_deploy.assert_called_once_with(
            uuid_value="1234-5678",
            naming_prefix="test-prefix",
            target_environment="production",
            region="us-east-1",
            instance="000",
            provider_config={"key": "value"},
        )


def test_callback_return_values_for_dict(fakedata):
    result, _ = callback_deploy_remote_state(
        key="any_key", value={}, **fakedata["kwargs"]
    )
    assert result is True


def test_callback_return_values_for_uuid(fakedata):
    result, _ = callback_deploy_remote_state(
        key="key1", value="value1", **fakedata["kwargs"]
    )
    assert result is False
