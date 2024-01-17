import os


def strtobool(value: str) -> bool:
    """Turns a truthy or falsy case-insensitive string into a boolean. Previously this was provided by distutils, but that has been deprecated.

    Args:
        value (str): Input value to turn into a boolean.

    Raises:
        ValueError: Raised if the input string isn't one of our recognized truthy or falsy values.

    Returns:
        bool: Result of determining truthiness or falsiness.
    """
    value = str(value)
    truthy_values = ["y", "yes", "t", "true", "on", "1"]
    falsy_values = ["n", "no", "f", "false", "off", "0"]
    if value.lower() in truthy_values:
        return True
    elif value.lower() in falsy_values:
        return False
    else:
        raise ValueError(
            f"Provided string '{value}' was not valid! Must be one of {truthy_values + falsy_values}"
        )


def get_bool_env_var(env_var_name: str, default_value: bool) -> bool:
    """Gets a value from an environment variable if it is set, and returns the default_value otherwise.

    Args:
        env_var_name (str): Name of the environment variable to pull from.
        default_value (bool): Replacement value if the environment variable is not set.

    Raises:
        ValueError: Raises from internal comparison if the value in the environment variable isn't one of our recognized truthy or falsy values.

    Returns:
        bool: Result of determining truthiness or falsiness.
    """
    return strtobool(os.environ.get(env_var_name, default=default_value))


UPDATE_CHECK = get_bool_env_var("LAUNCH_CLI_UPDATE_CHECK", False)
UPDATE_ALLOW_PRERELEASE = get_bool_env_var("LAUNCH_CLI_UPDATE_ALLOW_PRERELEASE", False)
