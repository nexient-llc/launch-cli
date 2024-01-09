import logging
import sys

import click


@click.group(name="cli", invoke_without_command=True)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    show_default=True,
    default=False,
    help="Increase verbosity of all subcommands",
)
@click.option(
    "--version",
    is_flag=True,
    show_default=True,
    default=False,
    help="Prints the current version of the tool and immediately exits.",
)
def cli(verbose, version):
    """Launch CLI tooling to help automate common tasks performed by Launch engineers and their clients."""
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(asctime)s\t%(name)s\t%(levelname)s\t%(message)s",
        datefmt="%F %T %Z",
    )
    if version:
        from launch import SEMANTIC_VERSION

        logging.info(f"Launch CLI Version {SEMANTIC_VERSION}")
        sys.exit(0)


from .github import github_group

cli.add_command(github_group)
