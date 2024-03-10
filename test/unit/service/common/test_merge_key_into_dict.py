import json
import os
import tempfile
from pathlib import Path

import pytest

from launch.service.common import merge_key_into_dict


def test_merge_key_into_dict_simple_merge():
    source = {"a": 1, "b": 2}
    target = {}
    merge_key = "a"
    merge_key_into_dict(source, target, merge_key)
    assert target == {"a": 1}


def test_merge_key_into_dict_nested_merge():
    source = {"parent": {"child": {"a": 1}}}
    target = {}
    merge_key = "a"
    merge_key_into_dict(source, target, merge_key, path=None)
    assert target == {"parent": {"child": {"a": 1}}}


def test_merge_key_into_dict_no_merge_key_present():
    source = {"a": 1}
    target = {}
    merge_key = "b"
    merge_key_into_dict(source, target, merge_key, path=None)
    assert target == {}


def test_merge_key_into_dict_path_creation():
    source = {"level1": {"level2": {"a": 1}}}
    target = {"level1": {}}
    merge_key = "a"
    merge_key_into_dict(source, target, merge_key, path=None)
    assert target == {"level1": {"level2": {"a": 1}}}


def test_merge_key_into_dict_with_existing_data():
    source = {"level1": {"level2": {"a": 1}}}
    target = {"level1": {"level2": {"b": 2}}}
    merge_key = "a"
    merge_key_into_dict(source, target, merge_key, path=None)
    assert target == {"level1": {"level2": {"b": 2, "a": 1}}}
