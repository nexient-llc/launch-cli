from launch.cli.entrypoint import cli
from launch.cli.github.access.commands import set_default
from launch.cli.github.hooks.commands import create
from launch.cli.github.version.commands import apply, predict


def test_cli_help(cli_runner):
    result = cli_runner.invoke(cli, "--help")
    assert "Launch CLI" in result.output
    assert not result.exception


def test_github_access_command_help(cli_runner):
    result = cli_runner.invoke(set_default, "--help")
    assert "set-default" in result.output
    assert not result.exception


def test_github_hooks_command_help(cli_runner):
    result = cli_runner.invoke(create, "--help")
    assert "create" in result.output
    assert not result.exception


def test_github_version_predict_help(cli_runner):
    result = cli_runner.invoke(predict, "--help")
    assert "predict" in result.output
    assert not result.exception


def test_github_version_apply_help(cli_runner):
    result = cli_runner.invoke(apply, "--help")
    assert "creates and pushes" in result.output
    assert not result.exception
