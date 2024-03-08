import json
import tempfile
from pathlib import Path

import pytest

from launch.automation.provider.az.functions import callback_deploy_remote_state
