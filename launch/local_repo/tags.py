import pathlib
from contextlib import suppress

from git.repo import Repo
from semver import Version


def read_tags(repo_path: pathlib.Path) -> list[str]:
    try:
        repo_instance = Repo(path=repo_path)
    except Exception as e:
        raise RuntimeError(
            f"Failed to get a Repo instance from path {repo_path}: {e}"
        ) from e
    return [tag.name for tag in repo_instance.tags]


def read_semantic_tags(repo_path: pathlib.Path) -> list[Version]:
    all_tags = read_tags(repo_path=repo_path)
    semver_tags: list[Version] = []
    for tag in all_tags:
        # If the tag doesn't align with SemVer, we can't do anything with it, but don't need to raise.
        with suppress(ValueError):
            semver_tags.append(Version.parse(tag))
    return semver_tags
