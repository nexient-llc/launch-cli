import os
from unittest.mock import MagicMock

import pytest

from launch.automation.common.functions import traverse_with_callback


@pytest.fixture
def callback_mock(mocker):
    return mocker.MagicMock(return_value=(True, {}))


def test_traverse_with_empty_dict(callback_mock):
    result = traverse_with_callback({}, callback_mock)
    callback_mock.assert_not_called()
    assert result == {}


def test_traverse_with_simple_dict(callback_mock):
    simple_dict = {"key1": "value1", "key2": "value2"}
    traverse_with_callback(simple_dict, callback_mock)
    assert callback_mock.call_count == 2


def test_traverse_with_nested_dict(callback_mock):
    nested_dict = {"level1": {"level2": {"key": "value"}}}
    traverse_with_callback(nested_dict, callback_mock)
    assert callback_mock.call_count == 3
