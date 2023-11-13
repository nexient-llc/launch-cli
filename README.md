# Launch CLI

Simple CLI utility for common Launch tasks. This is intended to be built upon as new tasks are discovered.

## Prereqs

- python >= 3.11
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
1. Clone this repository to your machine.
2. Enter the repostiory's directory and issue the command `python3 -m pip install .`
3. You can now use the `launch` command family from your CLI.


### Development Installation

1. Clone this repository to your machine.
2. Enter the repostiory's directory and issue the command `python3 -m pip install -e '.[dev]'` to create an editable installation.
3. You can now use the `launch` command family from your CLI, and changes made to the repository should be available the next time you run the CLI command.

## Usage

Currently, we expose one useful command:

```sh
$ launch github access set-default
```

This command takes several CLI arguments, you can issue `--help` for an explanation.
