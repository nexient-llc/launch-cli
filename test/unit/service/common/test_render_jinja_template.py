from pathlib import Path
from unittest.mock import MagicMock, mock_open, patch

import pytest

from launch.service.common import render_jinja_template


@patch("launch.service.common.Environment")
@patch("launch.service.common.logger")
@patch("launch.service.common.open", new_callable=mock_open)
def test_render_jinja_template(mock_open, mock_logger, mock_Environment):
    template_path = Path("/path/to/template.j2")
    destination_dir = Path("/path/to/destination")
    file_name = "output.txt"
    template_data = {"data": {"key": "value", "config": {"platform": {}}}}

    mock_template = MagicMock()
    mock_template.render.return_value = "Rendered template content"
    mock_env_instance = mock_Environment.return_value
    mock_env_instance.get_template.return_value = mock_template

    render_jinja_template(template_path, destination_dir, file_name, template_data)

    mock_Environment.assert_called_once()
    mock_env_instance.get_template.assert_called_once_with(template_path.name)
    mock_template.render.assert_called_once_with(
        {
            "data": {
                "key": "value",
                "path": str(destination_dir),
                "config": {"platform": {}, "dir_dict": None},
            }
        }
    )
    mock_logger.info.assert_called_once_with(
        f"Rendered template saved to {destination_dir / file_name}"
    )

    mock_open.assert_called_once_with(destination_dir / file_name, "w")
    mock_open.return_value.__enter__.return_value.write.assert_called_once_with(
        "Rendered template content"
    )
