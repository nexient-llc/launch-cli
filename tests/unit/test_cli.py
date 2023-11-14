from launch.cli.entrypoint import cli
from launch.cli.github.access.commands import set_default


def test_cli_help(cli_runner):
    result = cli_runner.invoke(cli, "--help")
    assert "Launch CLI" in result.output
    assert not result.exception


def test_github_access_command_help(cli_runner):
    result = cli_runner.invoke(set_default, "--help")
    assert "set-default" in result.output
    assert not result.exception
