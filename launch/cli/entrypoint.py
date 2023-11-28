import logging

import click


@click.group(name="cli")
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    show_default=True,
    default=False,
    help="Increase verbosity of all subcommands",
)
def cli(verbose):
    """Launch CLI tooling to help automate common tasks performed by Launch engineers and their clients."""
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(asctime)s\t%(name)s\t%(levelname)s\t%(message)s",
        datefmt="%F %T %Z",
    )


from .github import github_group

cli.add_command(github_group)
