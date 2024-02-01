from unittest.mock import patch, MagicMock, mock_open
import pytest
from pathlib import Path
from launch.service.common import render_template 

@pytest.fixture
def mock_env():
    mock_template = MagicMock()
    mock_env = MagicMock()
    mock_env.get_template.return_value = mock_template
    return mock_env, mock_template

def test_successful_rendering_and_file_creation(mock_env):
    env, mock_template = mock_env
    mock_template.render.return_value = "Output File: output.txt\nRendered Content"
    
    with patch("builtins.open", new_callable=mock_open()) as mock_file, \
         patch("launch.service.common.Path.mkdir") as mock_mkdir, \
         patch("launch.service.common.logging.Logger.info") as mock_logger:
        render_template("template.jinja", "/path/to/output", {"key": "value"}, env)
        
        mock_mkdir.assert_called_once()
        mock_file.assert_called_once_with(Path("/path/to/output/output.txt"), 'w')
        mock_file().write.assert_called_once_with("Rendered Content")
        mock_logger.assert_called()

def test_successful_rendering_and_file_creation(mock_env):
    env, mock_template = mock_env
    mock_template.render.return_value = "Output File: output.txt\nRendered Content"
    
    with patch("builtins.open", mock_open()) as mock_file, \
         patch("launch.service.common.Path.mkdir") as mock_mkdir, \
         patch("launch.service.common.logging.Logger.info") as mock_logger:
        render_template("template.jinja", "/path/to/output", {"key": "value"}, env)
        
        mock_mkdir.assert_called_once_with(exist_ok=True)
        mock_file.assert_called_once_with(Path("/path/to/output/output.txt"), 'w')
        mock_file().write.assert_called_once_with("Rendered Content")
        mock_logger.assert_called()

def test_exception_for_missing_output_file_name(mock_env):
    env, mock_template = mock_env
    mock_template.render.return_value = "No output file specified"
    
    with pytest.raises(RuntimeError) as excinfo:
        render_template("template.jinja", "/path/to/output", {"key": "value"}, env)
    assert "No output file name found in template: template.jinja" in str(excinfo.value)
