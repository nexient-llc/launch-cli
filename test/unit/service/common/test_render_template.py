from unittest.mock import patch, MagicMock, mock_open
import pytest
from launch.service.common import render_template

# Test successful template rendering and file writing
@patch('launch.service.common.os.makedirs')
@patch('launch.service.common.open', new_callable=mock_open)
@patch('launch.service.common.logger.info')
def test_render_template_success(mock_logger, mock_file_open, mock_makedirs):
    env = MagicMock()
    template_content = "Output File: test_output.txt\nContent to write"
    env.get_template.return_value.render.return_value = template_content
    template_name = "test_template"
    output_path = "/output/path"
    data = {"key": "value"}

    render_template(template_name, output_path, data, env)

    mock_logger.assert_called_once_with(f"Rendered {template_name} to /output/path/test_output.txt")
    mock_makedirs.assert_called_once_with('/output/path', exist_ok=True)
    mock_file_open.assert_called_once_with('/output/path/test_output.txt', 'w')
    handle = mock_file_open()
    handle.write.assert_called_once_with('Content to write')

# Test no output file name found in template
@patch('launch.service.common.os.makedirs')
@patch('launch.service.common.open', new_callable=mock_open)
@patch('launch.service.common.logger.info')
def test_render_template_no_output_file(mock_logger, mock_file_open, mock_makedirs):
    env = MagicMock()
    template_content = "No output file info"
    env.get_template.return_value.render.return_value = template_content
    template_name = "test_template"
    output_path = "/output/path"
    data = {"key": "value"}

    with pytest.raises(RuntimeError) as excinfo:
        render_template(template_name, output_path, data, env)

    assert "No output file name found in template: test_template" in str(excinfo.value)


@patch('launch.service.common.os.makedirs')
@patch('launch.service.common.open', new_callable=mock_open)
@patch('launch.service.common.logger.info')
def test_render_template_various_contents(mock_logger, mock_file_open, mock_makedirs):
    env = MagicMock()
    template_contents = [
        "Output File: file1.txt\nFirst content",
        "Content without output file name",
        "Output File: file2.txt\nSecond content"
    ]
    env.get_template.return_value.render.side_effect = template_contents
    template_name = "test_template"
    output_path = "/output/path"
    data = {"key": "value"}

    render_template(template_name, output_path, data, env)
    mock_file_open.assert_called_with('/output/path/file1.txt', 'w')
    handle = mock_file_open()
    handle.write.assert_called_with('First content')

    with pytest.raises(RuntimeError):
        render_template(template_name, output_path, data, env)

    render_template(template_name, output_path, data, env)
    mock_file_open.assert_called_with('/output/path/file2.txt', 'w')
    handle = mock_file_open()
    handle.write.assert_called_with('Second content')
