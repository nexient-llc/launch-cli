import json
import logging
import re
import shutil
from pathlib import Path
from typing import List

import yaml
from jinja2 import Environment, FileSystemLoader

from launch import BUILD_DEPEPENDENCIES_DIR, SERVICE_SKELETON, SKELETON_BRANCH

logger = logging.getLogger(__name__)


def create_directories(
    base_path: str, platform_data: dict, current_path: str = "platform"
) -> None:
    if isinstance(platform_data, dict):
        for key, value in platform_data.items():
            if isinstance(value, dict):
                next_path = Path(base_path) / current_path / key
                next_path.mkdir(parents=True, exist_ok=True)
                create_directories(base_path, value, Path(current_path) / key)
            else:
                next_path = Path(base_path) / current_path
                next_path.mkdir(parents=True, exist_ok=True)
    elif isinstance(platform_data, list):
        pass


def copy_properties_files(
    base_path: Path, platform_data: dict, current_path: Path = Path("platform")
) -> dict:
    if isinstance(platform_data, dict):
        for key, value in platform_data.items():
            if isinstance(value, dict):
                copy_properties_files(
                    base_path=base_path,
                    platform_data=value,
                    current_path=current_path / Path(key),
                )
            elif key == "properties_file":
                dest_path = base_path / current_path
                dest_path.mkdir(parents=True, exist_ok=True)
                logger.info(f"Copying {base_path}/{value} to {dest_path}")
                shutil.copy(
                    base_path / Path(value), dest_path / Path("terraform.tfvars")
                )

                relative_path = str(dest_path).removeprefix(base_path)
                platform_data[
                    key
                ] = f"{BUILD_DEPEPENDENCIES_DIR}/{relative_path}/{value.split('/')[-1]}"
    elif isinstance(platform_data, list):
        pass
    return platform_data


def list_jinja_templates(base_dir: str) -> tuple:
    base_path = Path(base_dir)
    template_paths = []
    modified_paths = []
    pattern = re.compile(r"\{\{.*?\}\}")

    for jinja_file in base_path.rglob("*.j2"):
        modified_path = pattern.sub("*", str(jinja_file))
        modified_path = modified_path.replace(str(base_path), "")
        modified_path = modified_path.lstrip("/")
        modified_paths.append(modified_path)
        template_paths.append(jinja_file.as_posix())

    return template_paths, modified_paths


def render_jinja_template(
    template_path: Path,
    destination_dir: str,
    file_name: str,
    template_data: dict = {"data": None},
) -> None:
    if not template_data.get("data"):
        template_data["data"] = {}

    env = Environment(loader=FileSystemLoader(template_path.parent))
    template = env.get_template(template_path.name)
    template_data["data"]["path"] = str(destination_dir)
    output = template.render(template_data)
    destination_path = destination_dir / file_name

    with open(destination_path, "w") as f:
        f.write(output)
    logger.info(f"Rendered template saved to {destination_path}")


def create_specific_path(base_path: Path, path_parts: list) -> list:
    specific_path = base_path.joinpath(*path_parts)
    specific_path.mkdir(parents=True, exist_ok=True)
    return [specific_path]


def expand_wildcards(
    current_path: Path,
    remaining_parts: List[str],
) -> List[Path]:
    """Expand wildcard paths."""
    if not remaining_parts:
        return [current_path]

    next_part, *next_remaining_parts = remaining_parts
    if next_part == "*":
        if not next_remaining_parts:
            return list_directories(current_path)
        else:
            all_subdirs = []
            for sub_path in list_directories(current_path):
                all_subdirs.extend(expand_wildcards(sub_path, next_remaining_parts))
            return all_subdirs
    else:
        next_path = current_path / next_part
        next_path.mkdir(exist_ok=True)
        return expand_wildcards(next_path, next_remaining_parts)


def list_directories(directory: Path) -> List[Path]:
    """List subdirectories in a given directory."""
    return [sub_path for sub_path in directory.iterdir() if sub_path.is_dir()]


def find_dirs_to_render(base_path: str, path_parts: list) -> list:
    base_path_obj = Path(base_path)
    if "*" not in path_parts:
        return create_specific_path(base_path_obj, path_parts)
    else:
        return expand_wildcards(base_path_obj, path_parts)


def copy_and_render_templates(
    base_dir: str, template_paths: list, modified_paths: list, context_data: dict = {}
) -> None:
    base_path = Path(base_dir)
    for template_path_str, modified_path in zip(template_paths, modified_paths):
        template_path = Path(template_path_str)
        file_name = template_path.name.replace(".j2", "")
        path_parts = modified_path.strip("/").split("/")
        dirs_to_render = find_dirs_to_render(base_path, path_parts[:-1])
        for dir_path in dirs_to_render:
            render_jinja_template(template_path, dir_path, file_name, context_data)


def write_text(
    path: Path, data: dict, output_format: str = "json", indent: int = 4
) -> None:
    if output_format == "json":
        serialized_data = json.dumps(data, indent=indent)
    elif output_format == "yaml":
        serialized_data = yaml.dump(data, indent=indent)
    else:
        message = f"Unsupported output format: {output_format}"
        logger.error(message)
        raise ValueError(message)

    path.write_text(serialized_data)


def input_data_validation(input_data: dict) -> dict:
    if not "skeleton" in input_data:
        input_data["skeleton"]: dict[str, str] = {}
    if not "url" in input_data["skeleton"] or not input_data["skeleton"]["url"]:
        logger.info(f"No skeleton url provided, using default: {SERVICE_SKELETON}")
        input_data["skeleton"]["url"] = SERVICE_SKELETON
    if not "tag" in input_data["skeleton"] or not input_data["skeleton"]["tag"]:
        logger.info(f"No skeleton tag provided, using default: {SKELETON_BRANCH}")
        input_data["skeleton"]["tag"] = SKELETON_BRANCH

    return input_data
