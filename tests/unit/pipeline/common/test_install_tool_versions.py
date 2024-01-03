import pytest

from unittest.mock import patch, mock_open
from launch.pipeline.common.functions import *


@pytest.fixture(scope="function")

# install_tool_versions
def test_install_tool_versions_success():
    mock_file_content = "python 3.8.1\nnodejs 12.18.3"
    with patch('subprocess.run') as mock_run, \
         patch('open', mock_open(read_data=mock_file_content)), \
         patch('os.chdir') as mock_chdir:
        install_tool_versions()
        assert mock_run.call_count == 3  # Two plugins and one 'asdf install'
        mock_chdir.assert_called_once()

def test_install_tool_versions_exception():
    with patch('subprocess.run', side_effect=Exception('Test Error')), \
         patch('open', mock_open(read_data="")), \
         patch('os.chdir') as mock_chdir:
        with pytest.raises(RuntimeError):
            install_tool_versions()