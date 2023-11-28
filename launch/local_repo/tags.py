import logging
import pathlib
from contextlib import suppress

from git import TagReference
from git.repo import Repo
from semver import Version

logger = logging.getLogger(__name__)


def acquire_repo(repo_path: pathlib.Path) -> Repo:
    try:
        return Repo(path=repo_path)
    except Exception as e:
        raise RuntimeError(
            f"Failed to get a Repo instance from path {repo_path}: {e}"
        ) from e


def read_tags(repo_path: pathlib.Path) -> list[str]:
    repo_instance = acquire_repo(repo_path=repo_path)
    all_tags = [tag.name for tag in repo_instance.tags]
    logger.debug(f"Discovered {len(all_tags)} tags")
    return all_tags


def read_semantic_tags(repo_path: pathlib.Path) -> list[Version]:
    all_tags = read_tags(repo_path=repo_path)
    semver_tags: list[Version] = []
    for tag in all_tags:
        try:
            parsed_tag = Version.parse(tag)
            semver_tags.append(parsed_tag)
        except ValueError:
            logger.debug(f"Dropping {tag=}, does not conform to semantic version")
    logger.debug(f"Narrowed to {len(semver_tags)} tags")
    return semver_tags


def create_version_tag(repo_path: pathlib.Path, version: Version) -> TagReference:
    repo_instance = acquire_repo(repo_path=repo_path)
    new_tag = repo_instance.create_tag(str(version))
    logger.info(f"Created {new_tag=}")
    return new_tag


def push_version_tag(
    repo_path: pathlib.Path, tag: TagReference, origin_name: str = "origin"
):
    repo_instance = acquire_repo(repo_path=repo_path)
    repo_instance.remote(origin_name).push(tag.name)
    logger.debug(f"Pushed {tag=} to {origin_name=}")
