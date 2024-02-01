import unittest
from pathlib import Path
from launch.service.common import get_last_dir


def test_file_in_nested_directory():
    path = Path("/path/to/nested/file.txt")
    assert get_last_dir(path) == "nested", "Failed: test_file_in_nested_directory"

def test_directory_path():
    path = Path("/path/to/nested/directory/")
    assert get_last_dir(path) == "nested", "Failed: test_directory_path"

def test_root_directory():
    path = Path("/")
    assert get_last_dir(path) is None, "Failed: test_root_directory"

def test_non_pathlib_input():
    path = "/path/to/nested/file.txt"
    assert get_last_dir(path) is None, "Failed: test_non_pathlib_input"
