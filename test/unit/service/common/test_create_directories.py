import tempfile
import json
import pytest
import os
from pathlib import Path
from launch.service.common import create_directories


def test_create_nested_directories(fakedata):
    with tempfile.TemporaryDirectory() as temp_dir:
        base_path = temp_dir
        create_directories(base_path, fakedata)
        assert (Path(base_path) / "platform/service/sandbox/us-east-2").exists()
        assert (Path(base_path) / "platform/pipeline").exists()

def test_create_single_directory():
    with tempfile.TemporaryDirectory() as temp_dir:
        base_path = temp_dir
        platform_data = {"webhook": {}}
        create_directories(base_path, platform_data)
        assert (Path(base_path) / "platform/webhook").exists()

def test_empty_platform_data():
    with tempfile.TemporaryDirectory() as temp_dir:
        base_path = temp_dir
        platform_data = {}
        create_directories(base_path, platform_data)
        assert len(list(Path(base_path).glob('**'))) == 1

def test_non_dict_platform_data():
    with tempfile.TemporaryDirectory() as temp_dir:
        base_path = temp_dir
        platform_data = []
        create_directories(base_path, platform_data)
        assert len(list(Path(base_path).glob('**'))) == 1
