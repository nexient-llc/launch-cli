from test.unit.automation.helm.fixtures import isolated_helm_chart_with_dependencies

from src.launch.automation.helm.functions import extract_dependencies_from_chart


def test_extract_dependencies(isolated_helm_chart_with_dependencies):
    extracted_dependencies = extract_dependencies_from_chart(
        isolated_helm_chart_with_dependencies
    )
    assert len(extracted_dependencies) == 1
    assert extracted_dependencies[0]["name"] == "helm-library"
    assert extracted_dependencies[0]["version"] == "^2.0.0"
    assert extracted_dependencies[0]["repository"] == "file://../../charts/helm-library"
