from pathlib import Path
from unittest.mock import MagicMock, call, patch

import pytest

from launch.service.common import BUILD_DEPEPENDENCIES_DIR, copy_properties_files


@pytest.fixture
def platform_data():
    return {
        "platform": {
            "componentA": {
                "properties_file": "config/componentA.properties",
            },
            "componentB": {
                "subcomponentB1": {
                    "properties_file": "config/subcomponentB1.properties",
                },
            },
        },
        "base_path": "/path/to/source",
        "dest_base_path": "/path/to/dest/",
    }


def test_copy_properties_files(platform_data):
    base_path = platform_data["base_path"]
    dest_base_path = platform_data["dest_base_path"]

    with patch("launch.service.common.shutil.copy") as mock_copy, patch(
        "pathlib.Path.mkdir"
    ) as mock_mkdir:
        result = copy_properties_files(
            platform_data=platform_data["platform"],
            base_path=base_path,
            dest_base_path=dest_base_path,
        )

        expected_mkdir_calls = [
            call(parents=True, exist_ok=True),
            call(parents=True, exist_ok=True),
        ]
        mock_mkdir.assert_has_calls(expected_mkdir_calls, any_order=True)

        expected_copy_calls = [
            call(
                f"{base_path}/config/componentA.properties",
                f"{dest_base_path}/path/to/source/platform/componentA",
            ),
            call(
                f"{base_path}/config/subcomponentB1.properties",
                f"{dest_base_path}/path/to/source/platform/componentB/subcomponentB1",
            ),
        ]
        mock_copy.assert_has_calls(expected_copy_calls, any_order=True)

        expected_result = {
            "componentA": {
                "properties_file": f"{BUILD_DEPEPENDENCIES_DIR}/platform/componentA/componentA.properties",
            },
            "componentB": {
                "subcomponentB1": {
                    "properties_file": f"{BUILD_DEPEPENDENCIES_DIR}/platform/componentB/subcomponentB1/subcomponentB1.properties",
                },
            },
        }
        assert result == expected_result
