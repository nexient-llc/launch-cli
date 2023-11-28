# Launch CLI

Simple CLI utility for common Launch tasks. This is intended to be built upon as new tasks are discovered.

## Prerequisites

- asdf-vm
- A GitHub account

## Getting Started

To use this tool, you will need to create a GitHub Personal Access Token (PAT) if you have not already done so. Ensure the PAT has sufficient permissions for your use case.

More information on GitHub PATs can be found [here](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens).

The PAT must be provided to this script through the `GITHUB_TOKEN` environment variable. Alternate credential stores are not currently supported.

### Generating a PAT

To generate a PAT, visit your GitHub settings page, then navigate to Developer Tools, and finally Personal Access Tokens (https://github.com/settings/tokens).

Currently, this tool has been tested with "Token (classic)" PATs. It may be possible to use a fine-grained PAT, if you manage to do this please let us know!

Currently, this tool utilizes the `repo` scope. Additional scopes may be required in the future as the capabilities of the tool expand.

## Installation

### End User Installation

This assumes that the end user is utilizing the standard ~/.venv-dso environment that gets created when setting up a development environment using our Makefiles.

1. Clone this repository to your machine and enter the repository's directory.
2. Run `asdf install` to ensure you have Python 3.11 available. If you receive an error about a missing plugin, issue `asdf plugin add python` first.
3. Issue the command `python3 -m pip install .` to install the package.
4. You can now use the `launch` command family from your CLI.

### Development Installation

1. Clone this repository to your machine and enter the repository's directory.
2. Run `asdf install` to ensure you have Python 3.11 available. If you receive an error about a missing plugin, issue `asdf plugin add python` first.
3. Optionally, but highly recommended, create a new virtual environment and activate it with `python3.11 -m venv .venv && source .venv/bin/activate`.
4. Issue the command `python3 -m pip install -e '.[dev]'` to create an editable installation.
5. You can now use the `launch` command family from your CLI, and changes made to most code should be available the next time you run the CLI command, but changes to the entrypoint or pyproject.toml may require that you issue the pip install command again to update the generated shortcut.

### ZSH-specific configuration

If you use ZSH as your shell, you'll need to make one further modification. By default, ZSH allows you to change directories without entering the cd command, which is a problem if you have a directory name that shadows the name of the command you're trying to run! Edit your ~/.zshrc file to include the following:

```sh
# Disables changing directory without issuing the cd command
unsetopt autocd
```

Upon sourcing the file or restarting, this will stop your shell from descending into the launch/ directory when your current working directory is the root of this repository.

## Usage

Once installed, you can use the `launch` command from your shell. The `launch` command provides integrated helptext, which can be viewed by issuing the `--help` flag, like so:

```sh
$ launch --help
Usage: launch [OPTIONS] COMMAND [ARGS]...

  Launch CLI tooling to help automate common tasks performed by Launch
  engineers and their clients.

Options:
  -v, --verbose  Increase verbosity of all subcommands
  --help         Show this message and exit.

Commands:
  github  Command family for GitHub-related tasks.
  ...
```

We started with a group of commands under `github`, but you should expect the list of available commands to grow as the tooling expands to cover more of our use cases. To dig into the commands (or subgroups) available, you may issue the `--help` flag on a subcommand in the same way to explore a group of commands:

```sh
$ launch github --help
Usage: launch github [OPTIONS] COMMAND [ARGS]...

  Command family for GitHub-related tasks.

Options:
  --help  Show this message and exit.

Commands:
  access   Command family for dealing with GitHub access.
  hooks    Command family for dealing with GitHub webhooks.
  version  Command family for dealing with GitHub versioning.
```

One very important thing to keep in mind is that options correspond to the group or command and cannot be issued in arbitrary places in the command. To use the `--verbose` flag to increase the output, you must place it following the `launch` command and before any subcommands, as shown below:

```sh
launch --verbose github access ...
```
