import logging
import re
import subprocess

logger = logging.getLogger(__name__)


def callback_deploy_remote_state(
    key,
    value,
    **kwargs,
) -> bool:
    if isinstance(value, dict):
        return False
    elif key == "uuid":
        try:
            path_array = kwargs["current_path"].parts
            deploy_remote_state(
                uuid_value=value,
                naming_prefix=kwargs["naming_prefix"],
                target_environment=kwargs["target_environment"],
                region=path_array[-2],
                instance=path_array[-1],
                provider_config=kwargs["provider_config"],
            )
        except KeyError as e:
            message = f"Missing key in kwargs: {e}"
            logger.error(message)
            raise RuntimeError(message) from e
    return True


def deploy_remote_state(
    uuid_value: str,
    naming_prefix: str,
    target_environment: str,
    region: str,
    instance: str,
    provider_config: dict,
) -> None:
    run_list = ["make"]
    provider = provider_config["provider"]

    stripped_name = re.sub("[\W_]+", "", naming_prefix[0:16])
    storage_account_name = f"{stripped_name}{uuid_value}"
    if naming_prefix:
        run_list.append(f"NAME_PREFIX={naming_prefix}")
    if region:
        run_list.append(f"REGION={region}")
    if target_environment:
        run_list.append(f"ENVIRONMENT={target_environment}")
    if instance:
        run_list.append(f"ENV_INSTANCE={instance}")

    if provider in provider_config:
        if "container_name" in provider_config[provider]:
            run_list.append(
                f"CONTAINER_NAME={provider_config[provider].get('container_name')}"
            )
        if "storage_account_name" in provider_config[provider]:
            storage_account_name = f"STORAGE_ACCOUNT_NAME={provider_config[provider].get('storage_account_name')}"
        else:
            run_list.append(storage_account_name)
        if provider_config[provider].get("resource_group_name"):
            run_list.append(
                f"RESOURCE_GROUP_NAME={provider_config[provider].get('resource_group_name')}"
            )

    run_list.append(storage_account_name)
    run_list.append("terragrunt/remote_state/azure")

    logger.info(f"Running {run_list}")
    try:
        subprocess.run(run_list, check=True)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"An error occurred: {str(e)}") from e
