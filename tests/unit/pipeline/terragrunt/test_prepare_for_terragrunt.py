import git
from unittest.mock import patch, MagicMock
from  launch.pipeline.terragrunt.functions import prepare_for_terragrunt


# def test_prepare_for_terragrunt_success():
#     with patch('launch.pipeline.common.functions.git_clone', return_value=MagicMock(spec=git.Repo)) as mock_git_clone, \
#          patch('launch.pipeline.common.functions.os.chdir') as mock_chdir, \
#          patch('launch.pipeline.common.functions.git_checkout') as mock_git_checkout, \
#          patch('launch.pipeline.common.functions.install_tool_versions') as mock_install_tool_versions, \
#          patch('launch.pipeline.common.functions.set_netrc') as mock_set_netrc, \
#          patch('launch.pipeline.common.functions.copy_files_and_dirs') as mock_copy_files_and_dirs, \
#          patch('launch.pipeline.provider.aws.functions.assume_role') as mock_assume_role, \
#          patch('launch.pipeline.common.functions.check_git_changes', return_value=True) as mock_check_git_changes:

#         # Setup test data
#         repository_url = "https://github.com/example/repo.git"
#         override = {
#             'properties_suffix': 'suffix',
#             'tool_versions_file': 'file',
#             'machine': 'machine',
#             'login': 'login',
#             'infrastructure_dir': 'infra',
#             'environment_dir': 'env',
#             'main_branch': 'main'
#         }
#         provider_config = MagicMock(provider='aws')

#         # Call the function under test
#         prepare_for_terragrunt(
#             repository_url,
#             "git_token123",
#             "commit_sha123",
#             "target_environment",
#             provider_config,
#             False,  # skip_git
#             True,   # is_infrastructure
#             "/path",
#             override
#         )

#         # Assert that the mocks were called as expected
#         mock_git_clone.assert_called()
#         mock_chdir.assert_called()
#         mock_git_checkout.assert_called()
#         mock_install_tool_versions.assert_called_with(file=override['tool_versions_file'])
#         mock_set_netrc.assert_called_with(
#             password="git_token123", 
#             machine=override['machine'], 
#             login=override['login']
#         )
#         mock_copy_files_and_dirs.assert_called()
#         mock_assume_role.assert_called_with(
#             provider_config=provider_config, 
#             repository_name='repo', 
#             target_environment="target_environment"
#         )
#         mock_check_git_changes.assert_called_with(
#             repository=None, 
#             commit_id="commit_sha123", 
#             main_branch=override['main_branch'], 
#             directory=override['infrastructure_dir']
#         )
