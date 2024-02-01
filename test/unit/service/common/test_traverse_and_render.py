import pytest
from unittest.mock import patch, MagicMock, ANY
from launch.service.common import traverse_and_render
from pathlib import Path


@pytest.fixture
def mock_env():
    with patch("launch.service.common.render_template") as mock_render, \
         patch("launch.service.common.Path.mkdir") as mock_mkdir, \
         patch("launch.service.common.Path.iterdir") as mock_iterdir, \
         patch("launch.service.common.Path.is_dir", return_value=True) as mock_is_dir:
        mock_iterdir.return_value = [Path("dir1"), Path("dir2")]
        yield mock_render, mock_mkdir, mock_iterdir, mock_is_dir


def test_render_single_template(mock_env):
    mock_render, _, _, _ = mock_env
    structure = {"template": "template.j2"}
    traverse_and_render("/base/path", structure, {}, MagicMock())
    mock_render.assert_called_once_with("template.j2", "/base/path", {}, ANY)


def test_render_multiple_templates(mock_env):
    mock_render, _, _, _ = mock_env
    structure = {"template": ["template1.j2", "template2.j2"]}
    traverse_and_render("/base/path", structure, {}, MagicMock())
    assert mock_render.call_count == 2


def test_recursive_traversal_and_rendering(mock_env):
    _, mock_mkdir, _, _ = mock_env
    structure = {"nested": {"template": "nested_template.j2"}}
    traverse_and_render("/base/path", structure, {}, MagicMock())
    mock_mkdir.assert_called_with(exist_ok=True)


def test_dynamic_directory_names(mock_env):
    mock_render, _, mock_iterdir, mock_is_dir = mock_env
    structure = {"<dynamic>": {"template": "dynamic_template.j2"}}
    mock_iterdir.return_value = [Path("dynamic1"), Path("dynamic2")]
    mock_is_dir.return_value = True
    traverse_and_render("/base/path", structure, {}, MagicMock())
    assert mock_render.call_count == 2 
