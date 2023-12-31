import itertools
import logging

from semver import Version

logger = logging.getLogger(__name__)

BRANCH_DELIMITER = "/"

PATCH_NAME_PARTS = ["fix", "bug", "patch"]
MINOR_NAME_PARTS = ["feature"]
MAJOR_NAME_PARTS = []

BREAKING_CHARS = ["!"]
CAPITALIZE_FIRST_IS_BREAKING = True
DEFAULT_VERSION = Version(major=0, minor=1, patch=0)


class InvalidBranchNameException(Exception):
    pass


def split_delimiter(branch_name: str, delimiter: str | None = None) -> tuple[str, str]:
    if not delimiter:
        delimiter = BRANCH_DELIMITER

    separated = branch_name.split(sep=delimiter)
    if not len(separated) >= 2:
        raise InvalidBranchNameException(
            f"Branch name {branch_name} did not contain expected delimiter {delimiter}"
        )
    return separated[0], delimiter.join(separated[1:])


def latest_tag(tags: list[Version]) -> Version:
    return sorted(tags)[-1]


def predict_version(
    existing_tags: list[Version],
    branch_name: str,
    breaking_chars: list[str] | None = None,
    capitalize_first_is_breaking: bool | None = None,
):
    breaking_change: bool = False

    if not len(existing_tags):
        logger.warning(f"No tags exist on this repo, defaulting to {DEFAULT_VERSION}")
        return DEFAULT_VERSION

    latest_version = latest_tag(tags=existing_tags)
    logger.debug(f"Got {latest_version=} as the latest tag")

    if not breaking_chars:
        breaking_chars = BREAKING_CHARS

    if capitalize_first_is_breaking is None:
        capitalize_first_is_breaking = CAPITALIZE_FIRST_IS_BREAKING

    revision_type, _ = split_delimiter(branch_name=branch_name)

    valid_branch_revision_types = list(
        itertools.chain(MAJOR_NAME_PARTS, MINOR_NAME_PARTS, PATCH_NAME_PARTS)
    )

    logger.debug(f"Evaluating {revision_type=} against {valid_branch_revision_types=}")

    for breaking_char in breaking_chars:
        if breaking_char in revision_type:
            logger.debug(
                f"Detected {breaking_char=} in branch name, setting {breaking_change=}"
            )
            breaking_change = True
            revision_type = revision_type.strip(breaking_char)

    if revision_type.lower().strip() not in map(str.lower, valid_branch_revision_types):
        raise InvalidBranchNameException(
            f"Branch name {branch_name} is invalid, must case-insensitively match one of {valid_branch_revision_types}"
        )

    if capitalize_first_is_breaking:
        if revision_type[0] == revision_type[0].upper():
            logger.debug(
                f"Revision begins with a capital letter, setting {breaking_change=}"
            )
            breaking_change = True

    if breaking_change or revision_type.lower().strip() in MAJOR_NAME_PARTS:
        logger.debug("Bumping major version!")
        return latest_version.bump_major()
    elif revision_type.lower().strip() in MINOR_NAME_PARTS:
        logger.debug("Bumping minor version!")
        return latest_version.bump_minor()
    else:
        logger.debug("Bumping patch version!")
        return latest_version.bump_patch()
