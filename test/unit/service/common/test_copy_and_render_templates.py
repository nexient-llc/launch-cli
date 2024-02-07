import unittest
from unittest.mock import patch, call
from pathlib import Path
from launch.service.common import copy_and_render_templates

@patch('launch.service.common.find_dirs_to_render')
@patch('launch.service.common.render_jinja_template')
def test_copy_and_render_templates(mock_render_jinja_template, mock_find_dirs_to_render, fakedata):
    mock_find_dirs_to_render.side_effect = [['dir1', 'dir2'], ['dir3', 'dir4']]

    copy_and_render_templates(
        fakedata['copy_and_render']['base_dir'], 
        fakedata['copy_and_render']['template_paths'], 
        fakedata['copy_and_render']['modified_paths'],
        fakedata['copy_and_render']['context_data']
    )

    expected_calls = [
        call(Path('/path/to/template1.j2'), 'dir1', 'template1', fakedata['copy_and_render']['context_data']),
        call(Path('/path/to/template1.j2'), 'dir2', 'template1', fakedata['copy_and_render']['context_data']),
        call(Path('/path/to/template2.j2'), 'dir3', 'template2', fakedata['copy_and_render']['context_data']),
        call(Path('/path/to/template2.j2'), 'dir4', 'template2', fakedata['copy_and_render']['context_data'])
    ]
    mock_render_jinja_template.assert_has_calls(expected_calls, any_order=True)
