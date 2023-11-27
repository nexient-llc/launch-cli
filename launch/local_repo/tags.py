import pathlib
from contextlib import suppress

from git import TagReference
from git.repo import Repo
from semver import Version


def acquire_repo(repo_path: pathlib.Path) -> Repo:
    try:
        return Repo(path=repo_path)
    except Exception as e:
        raise RuntimeError(
            f"Failed to get a Repo instance from path {repo_path}: {e}"
        ) from e


def read_tags(repo_path: pathlib.Path) -> list[str]:
    repo_instance = acquire_repo(repo_path=repo_path)
    return [tag.name for tag in repo_instance.tags]


def read_semantic_tags(repo_path: pathlib.Path) -> list[Version]:
    all_tags = read_tags(repo_path=repo_path)
    semver_tags: list[Version] = []
    for tag in all_tags:
        # If the tag doesn't align with SemVer, we can't do anything with it, but don't need to raise.
        with suppress(ValueError):
            semver_tags.append(Version.parse(tag))
    return semver_tags


def create_version_tag(repo_path: pathlib.Path, version: Version) -> TagReference:
    repo_instance = acquire_repo(repo_path=repo_path)
    return repo_instance.create_tag(str(version))


def push_version_tag(
    repo_path: pathlib.Path, tag: TagReference, origin_name: str = "origin"
):
    repo_instance = acquire_repo(repo_path=repo_path)
    repo_instance.remote(origin_name).push(tag.name)
