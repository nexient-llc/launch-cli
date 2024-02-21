import pathlib
from typing import Generator

import pytest


@pytest.fixture
def isolated_helm_chart_with_dependencies(
    tmp_path,
) -> Generator[pathlib.Path, None, None]:
    source_file = pathlib.Path(__file__).parent.joinpath("data/simple_chart.yaml")
    destination_file = tmp_path.joinpath("Chart.yaml")
    destination_file.write_text(source_file.read_text())
    yield destination_file
