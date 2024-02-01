from unittest.mock import patch, MagicMock, call
import pytest
from pathlib import Path
from launch.service.common import create_dirs_and_copy_files


@pytest.fixture
def mock_utils():
    with patch("launch.service.common.Path.exists", MagicMock(return_value=True)) as mock_exists, \
         patch("launch.service.common.Path.mkdir") as mock_mkdir, \
         patch("launch.service.common.shutil.copy") as mock_copy, \
         patch("launch.service.common.logger.info") as mock_logger:
        yield {
            "exists": mock_exists,
            "mkdir": mock_mkdir,
            "copy": mock_copy,
            "logger": mock_logger
        }
def test_copy_existing_properties_file(mock_utils):
    base_path = "/fake/directory"
    nested_dict = {"properties_file": "/fake/source/terraform.tfvars"}
    create_dirs_and_copy_files(base_path, nested_dict)
    mock_utils["copy"].assert_called_once_with("/fake/source/terraform.tfvars", Path(base_path) / "terraform.tfvars")
    mock_utils["logger"].assert_called_with("Copied /fake/source/terraform.tfvars to /fake/directory/terraform.tfvars")

def test_raise_exception_for_nonexistent_properties_file():
    with patch("launch.service.common.Path.exists", MagicMock(return_value=False)):
        with pytest.raises(Exception) as excinfo:
            create_dirs_and_copy_files("/fake/directory", {"properties_file": "/fake/source/missing.tfvars"})
        assert "File not found: /fake/source/missing.tfvars" in str(excinfo.value)
