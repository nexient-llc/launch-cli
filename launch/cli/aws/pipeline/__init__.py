import click

from .commands import *


@click.group(name="pipeline")
def pipeline_group():
    """Command family for AWS Code-related tasks."""


pipeline_group.add_command(codebuild_status)
pipeline_group.add_command(pre_deploy_test)
pipeline_group.add_command(simulated_merge)
pipeline_group.add_command(terragrunt_deploy)
pipeline_group.add_command(terragrunt_plan)
pipeline_group.add_command(tf_post_deploy_functional_test)
pipeline_group.add_command(trigger_pipeline)
pipeline_group.add_command(build_container)
pipeline_group.add_command(conftest_container)
pipeline_group.add_command(launch_apply_semver)
pipeline_group.add_command(launch_predict_semver)
pipeline_group.add_command(lint_terraform_module)
pipeline_group.add_command(make_tfmodule_pre_deploy_test)
pipeline_group.add_command(maven_build)
pipeline_group.add_command(maven_test)
pipeline_group.add_command(python_integration_tests)
pipeline_group.add_command(python_unit_tests)
pipeline_group.add_command(auto_qa)
pipeline_group.add_command(certify_image)
pipeline_group.add_command(deploy_ecr_image)
pipeline_group.add_command(integration_test)
pipeline_group.add_command(publish_ecr_image)
