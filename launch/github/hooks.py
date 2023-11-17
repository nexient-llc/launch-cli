from github.Repository import Repository
from github.Hook import Hook


def create_hook(
    repo: Repository, 
    name: str, 
    config: dict[str, str], 
    events: list[str], 
    active: bool,
    dry_run: bool=True
) -> None:

    if not dry_run:
        print(
            f"Creating webhook on {repo.name} for repo {repo.url}"
        )
        repo.create_hook(
            name=name,
            config=config,
            events=events,
            active=active
        )
    else:
        print(
            f"Would have create webhook on {repo.name} for repo {repo.url}"
        )