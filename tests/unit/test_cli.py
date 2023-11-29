import pathlib

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


def test_github_version_apply_pipeline_safeguard_flag(
    cli_runner, example_github_repo, mocker
):
    new_branch = "not_main"
    current = example_github_repo.create_head(new_branch)
    current.checkout()
    pathlib.Path(example_github_repo.working_dir).joinpath("new.txt").write_text(
        "hello world"
    )
    example_github_repo.index.add("new.txt")
    example_github_repo.index.commit("Added new.txt")

    without_pipeline = cli_runner.invoke(
        apply,
        f"--repo-path {example_github_repo.working_dir} --source-branch feature/foo",
    )
    assert without_pipeline.exit_code == 1

    # This fails since our example github repo doesn't have a remote,
    # but if we get the message about a failing remote, we've gotten
    # far enough to validate this works.
    with_pipeline = cli_runner.invoke(
        apply,
        f"--repo-path {example_github_repo.working_dir} --source-branch feature/foo --pipeline",
    )
    assert "Remote named 'origin' didn't exist" in with_pipeline.stdout


def test_github_version_apply_bad_branch_name_exit_code(
    cli_runner, example_github_repo
):
    result = cli_runner.invoke(
        apply,
        f"--repo-path {example_github_repo.working_dir} --source-branch invalid/name",
    )
    assert result.exit_code == 1


def test_github_version_apply_tag_exists_exit_code(cli_runner, example_github_repo):
    result = cli_runner.invoke(
        apply,
        f"--repo-path {example_github_repo.working_dir} --source-branch feature/foo",
    )
    assert result.exit_code == 2
