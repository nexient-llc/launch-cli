# Launch CLI

Simple CLI utility for common Launch tasks. This is intended to be built upon as new tasks are discovered.

## Prerequisites

- Python 3.11+ and pip
- A GitHub account

## Getting Started

To use this tool, you will need to create a GitHub Personal Access Token (PAT) if you have not already done so.

The PAT must be provided to this script through the `GITHUB_TOKEN` environment variable. Alternate credential stores are planned but not yet supported.

### Generating a PAT

To generate a PAT that includes the necessary rights for `launch-cli`, follow [our instructions here](./docs/generating-a-token.md).

More information on GitHub PATs can be found [here](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens).

## Installation

There are two paths you can take to install, your choice will depend on what you intend to do with `launch-cli`. If you intend to use the tool's built-in commands as part of your normal role as a Launch engineer (this is the most common option), you should perform the **End User Installation** below. If you intend to develop additonal features for `launch-cli`, please follow the **Development Installation** below.

For either case, you will need to have Python 3.11 or greater installed on your system. How you choose to install that is up to you, but the installation steps assume you have an executable called `python3.11` in your path and the `pip` module installed.

### End User Installation

1. Issue the following command to install the latest version:

```sh
python3.11 -m pip install launch-cli
```

2. You can now use the `launch` command family from your CLI. Issue `launch --help` to confirm the launch command is available in your shell.

In the unlikely event that you need to install a specific version of `launch-cli` you may specify a version found on our [releases page](https://github.com/nexient-llc/launch-cli/releases):

```sh
python3.11 -m pip install launch-cli==0.1.0
```

### Development Installation

1. Clone this repository to your machine and enter the repository's directory.
2. Create a new virtual environment and activate it with `python3.11 -m venv .venv && source .venv/bin/activate`.
4. Issue the command `python3.11 -m pip install -e '.[dev]'` to create an editable installation.
5. You can now use the `launch` command family from your CLI, and changes made to most code should be available the next time you run the CLI command, but changes to the entrypoint or pyproject.toml may require that you issue the pip install command again to update the generated shortcut.

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
