import logging
import re
import shutil
from pathlib import Path

logger = logging.getLogger(__name__)

def create_dirs_and_copy_files(base_path, nested_dict, props_path_key='properties_file', props_file_name='terraform.tfvars'):
    for key, value in nested_dict.items():
        if key == props_path_key and isinstance(value, str):
            destination = Path(base_path) / props_file_name
            if Path(value).exists():
                shutil.copy(value, destination)
                logger.info(f"Copied {value} to {destination}")
            else:
                raise Exception(f"File not found: {value}")
        elif isinstance(value, dict):
            new_path = Path(base_path) / key
            if not Path(new_path).exists():
                Path(new_path).mkdir()
            create_dirs_and_copy_files(new_path, value)


def render_template(template_name, output_path, data, env):
    template = env.get_template(template_name)
    rendered_content = template.render(data={
        "path": output_path,
        "config": data
    })

    # Regular expression to extract output file name
    output_file_pattern = r'Output File: ([^\s]+)'
    match = re.search(output_file_pattern, rendered_content)
    if match:
        output_file_name = match.group(1)
        full_output_path = Path(output_path) / output_file_name
        content_to_write = re.sub(output_file_pattern, '', rendered_content, count=1).strip()
    else:
        raise RuntimeError(f"No output file name found in template: {template_name}")

    Path(Path(full_output_path).parent).mkdir(exist_ok=True)
    with open(full_output_path, 'w') as file:
        file.write(content_to_write)
    logger.info(f"Rendered {template_name} to {full_output_path}")


def traverse_and_render(base_path, structure, data, env):
    for key, value in structure.items():
        if key == "template":
            if isinstance(value, list):
                for template_name in value:
                    render_template(template_name, base_path, data, env)
            else:
                render_template(value, base_path, data, env)
        elif "<" in key and ">" in key:
            for dir_name in Path(base_path).iterdir():
                dir_path = Path(base_path) / dir_name
                if Path(dir_path).is_dir():
                    traverse_and_render(dir_path, value, data, env)
        elif isinstance(value, dict):
            new_path = Path(base_path) / key
            Path(new_path, exist_ok=True).mkdir(exist_ok=True)
            traverse_and_render(new_path, value, data, env)


def get_last_dir(path):
    if isinstance(path, Path):
        parts = path.parts
        return parts[-2] if len(parts) > 1 else None