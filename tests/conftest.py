import os

import pytest
from click import testing as click_testing


@pytest.fixture
def cli_runner():
    yield click_testing.CliRunner()


@pytest.fixture(scope="function")
def no_github_token(set_environment_variables):
    token_value = os.environ["GITHUB_TOKEN"]
    del os.environ["GITHUB_TOKEN"]
    yield
    os.environ["GITHUB_TOKEN"] = token_value


@pytest.fixture(scope="session", autouse=True)
def set_environment_variables():
    old_environment = dict(os.environ)
    os.environ.clear()
    os.environ.update({"GITHUB_TOKEN": "ghp_test_value"})
    yield
    os.environ.clear()
    os.environ.update(old_environment)
