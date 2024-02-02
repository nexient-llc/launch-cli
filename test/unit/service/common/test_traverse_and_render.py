from unittest.mock import patch, MagicMock, call
from launch.service.common import traverse_and_render


@patch('launch.service.common.render_template')
def test_traverse_and_render_single_template(mock_render_template):
    base_path = "/base/path"
    structure = {"template": "template1"}
    data = {"key": "value"}
    env = MagicMock()

    traverse_and_render(base_path, structure, data, env)

    mock_render_template.assert_called_once_with("template1", base_path, data, env)


@patch('launch.service.common.render_template')
def test_traverse_and_render_multiple_templates(mock_render_template):
    base_path = "/base/path"
    structure = {"template": ["template1", "template2"]}
    data = {"key": "value"}
    env = MagicMock()

    traverse_and_render(base_path, structure, data, env)

    mock_render_template.assert_any_call("template1", base_path, data, env)
    mock_render_template.assert_any_call("template2", base_path, data, env)


@patch('launch.service.common.os.listdir', return_value=["dir1", "dir2"])
@patch('launch.service.common.os.path.isdir', return_value=True)
@patch('launch.service.common.render_template')
def test_traverse_and_render_recursive(mock_render_template, mock_isdir, mock_listdir):
    base_path = "/base/path"
    structure = {"<dir>": {"template": "template1"}}
    data = {"key": "value"}
    env = MagicMock()

    traverse_and_render(base_path, structure, data, env)

    mock_listdir.assert_called_once_with(base_path)
    mock_isdir.assert_called()
    expected_calls = [
        call("template1", "/base/path/dir1", data, env),
        call("template1", "/base/path/dir2", data, env)
    ]
    mock_render_template.assert_has_calls(expected_calls, any_order=True)


@patch('launch.service.common.os.makedirs')
@patch('launch.service.common.render_template')
def test_traverse_and_render_create_dirs(mock_render_template, mock_makedirs):
    base_path = "/base/path"
    structure = {"dir1": {"template": "template1"}}
    data = {"key": "value"}
    env = MagicMock()

    traverse_and_render(base_path, structure, data, env)

    mock_makedirs.assert_called_once_with("/base/path/dir1", exist_ok=True)
    mock_render_template.assert_called_once_with("template1", "/base/path/dir1", data, env)
