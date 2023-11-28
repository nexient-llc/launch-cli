import logging
import os
from functools import cache

from github import Auth, Github

logger = logging.getLogger(__name__)


@cache
def read_github_token() -> str:
    try:
        return os.environ["GITHUB_TOKEN"]
    except KeyError:
        raise RuntimeError(
            "ERROR: The GITHUB_TOKEN environment variable is not set. You must set this environment variable with the contents of your GitHub Personal Access Token (PAT) to use this script."
        )


@cache
def github_headers() -> dict[str, str]:
    return {"Authorization": f"Bearer {read_github_token()}"}


def get_github_instance(token: str | None = None) -> Github:
    if not token:
        logger.debug("Token wasn't passed, reading from environment.")
        token = read_github_token()
    auth = Auth.Token(token)
    return Github(auth=auth)
