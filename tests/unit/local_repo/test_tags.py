import pytest
from git.repo import Repo
from semver import Version

from launch.local_repo.tags import read_semantic_tags, read_tags


def test_get_tags(tmp_path):
    temp_repo = Repo.init(path=tmp_path)
    tmp_path.joinpath("test.txt").write_text("Sample file")
    temp_repo.index.add("test.txt")
    temp_repo.index.commit("Added test.txt")
    temp_repo.create_tag("0.1.0")
    temp_repo.create_tag("not-semantic!")
    tags = read_tags(repo_path=tmp_path)
    assert len(tags) == 2
    assert "0.1.0" in tags
    assert "not-semantic!" in tags


def test_get_semantic_tags(tmp_path):
    temp_repo = Repo.init(path=tmp_path)
    tmp_path.joinpath("test.txt").write_text("Sample file")
    temp_repo.index.add("test.txt")
    temp_repo.index.commit("Added test.txt")
    temp_repo.create_tag("0.1.0")
    temp_repo.create_tag("not-semantic!")
    tags = read_semantic_tags(repo_path=tmp_path)
    assert len(tags) == 1
    assert Version.parse("0.1.0") in tags
