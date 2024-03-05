import logging
import subprocess

logger = logging.getLogger(__name__)


def deploy_remote_state(provider_config: dict, provider: str) -> None:
    run_list = ["make"]

    if provider_config[provider].get("name_prefix"):
        run_list.append(f"NAME_PREFIX={provider_config[provider].get('name_prefix')}")
    if provider_config[provider].get("region"):
        run_list.append(f"REGION={provider_config[provider].get('region')}")
    if provider_config[provider].get("environment"):
        run_list.append(f"ENVIRONMENT={provider_config[provider].get('environment')}")
    if provider_config[provider].get("env_instance"):
        run_list.append(f"ENV_INSTANCE={provider_config[provider].get('env_instance')}")
    if provider_config[provider].get("container_name"):
        run_list.append(
            f"CONTAINER_NAME={provider_config[provider].get('container_name')}"
        )
    if provider_config[provider].get("storage_account_name"):
        run_list.append(
            f"STORAGE_ACCOUNT_NAME={provider_config[provider].get('storage_account_name')}"
        )
    if provider_config[provider].get("resource_group_name"):
        run_list.append(
            f"RESOURCE_GROUP_NAME={provider_config[provider].get('resource_group_name')}"
        )

    run_list.append("terragrunt/remote_state/azure")

    logger.info(f"Running {run_list}")
    try:
        subprocess.run(run_list, check=True)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"An error occurred: {str(e)}") from e
