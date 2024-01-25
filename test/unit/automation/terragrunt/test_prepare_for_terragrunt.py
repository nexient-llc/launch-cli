import git
from unittest.mock import patch, MagicMock
from launch.automation.terragrunt.functions import prepare_for_terragrunt
from launch.automation.provider.aws.functions import assume_role
