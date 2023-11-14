# Shared fixtures go here.
import pytest
from click import testing as click_testing


@pytest.fixture
def cli_runner():
    yield click_testing.CliRunner()
