import subprocess
from unittest.mock import MagicMock, patch

import pytest

from launch.automation.provider.az.functions import deploy_remote_state
