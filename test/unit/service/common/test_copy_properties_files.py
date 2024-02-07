import pytest
import tempfile
import json
from pathlib import Path
from launch.service.common import copy_properties_files


def test_copy_properties_files_from_nested_dict(fakedata):
    with tempfile.TemporaryDirectory() as temp_dir:
        base_path = temp_dir
        temp_properties_file = Path(temp_dir) / "temp.properties"
        temp_properties_file.write_text("some properties")
        fakedata['service']['sandbox']['us-east-2']['properties_file'] = str(temp_properties_file)
        copy_properties_files(base_path, fakedata)

        dest_path = Path(temp_dir) / "platform/service/sandbox/us-east-2/temp.properties"
        assert dest_path.exists()

def test_non_dict_platform_data():
    with tempfile.TemporaryDirectory() as temp_dir:
        base_path = temp_dir
        platform_data = [] 
        copy_properties_files(base_path, platform_data)

        assert len(list(Path(temp_dir).glob('**/*'))) == 0

def test_properties_file_in_root_dict():
    with tempfile.TemporaryDirectory() as temp_dir:
        base_path = temp_dir
        temp_properties_file = Path(temp_dir) / "root.properties"
        temp_properties_file.write_text("root properties")

        platform_data = {
            "properties_file": str(temp_properties_file)
        }

        copy_properties_files(base_path, platform_data)

        dest_path = Path(temp_dir) / "platform/root.properties"
        assert dest_path.exists()
