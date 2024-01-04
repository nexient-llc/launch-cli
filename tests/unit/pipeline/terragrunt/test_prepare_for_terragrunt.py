import pytest
from unittest.mock import patch, MagicMock
from launch.pipeline.terragrunt.functions import *


@pytest.fixture
def mock_dependencies(mocker):
    mock_exists = mocker.patch('os.path.exists', return_value=True)
    mock_chdir = mocker.patch('os.chdir')
    mock_git_clone = mocker.patch('launch.pipeline.common.functions.git_clone', return_value=MagicMock())
    mock_git_checkout = mocker.patch('launch.pipeline.common.functions.git_checkout')
    mock_install_tool_versions = mocker.patch('launch.pipeline.common.functions.install_tool_versions')
    mock_set_netrc = mocker.patch('launch.pipeline.common.functions.set_netrc')
    mock_check_git_changes = mocker.patch('launch.pipeline.common.functions.check_git_changes', return_value=False)
    mock_copy_files_and_dirs = mocker.patch('launch.pipeline.common.functions.copy_files_and_dirs')
    mock_read_key_value_from_file = mocker.patch('launch.pipeline.common.functions.read_key_value_from_file', return_value="aws_profile")
    mock_aws_assume_role = mocker.patch('launch.pipeline.provider.aws.functions.assume_role')

    return {
        'mock_exists': mock_exists,
        'mock_chdir': mock_chdir,
        'mock_git_clone': mock_git_clone,
        'mock_git_checkout': mock_git_checkout,
        'mock_install_tool_versions': mock_install_tool_versions,
        'mock_set_netrc': mock_set_netrc,
        'mock_check_git_changes': mock_check_git_changes,
        'mock_copy_files_and_dirs': mock_copy_files_and_dirs,
        'mock_read_key_value_from_file': mock_read_key_value_from_file,
        'mock_aws_assume_role': mock_aws_assume_role
    }

def test_without_skip_git(mock_dependencies):
    repository_url = "https://github.com/example/repo.git"
    override = {
        'properties_suffix': 'suffix', 
        'tool_versions_file': 'file', 
        'machine': 'machine', 
        'login': 'login', 
        'infrastructure_dir': 'infra', 
        'environment_dir': 'env',
        'main_branch': 'main'
    }
    
    # Mock check_git_changes to return True to avoid triggering the RuntimeError
    mock_dependencies['mock_check_git_changes'].return_value = True

    prepare_for_terragrunt(
        repository_url,
        "token123",
        "commit123",
        "prod",
        MagicMock(provider='aws'),
        False, # skip_git
        True,  # is_infrastructure
        "/path",
        override
    )
    
    # Assertions for git_clone calls
    mock_dependencies['mock_git_clone'].assert_any_call(
        target_dir="repo",
        clone_url=repository_url
    )

    # Assertions for git_checkout call
    mock_dependencies['mock_git_checkout'].assert_called_once_with(
        repository=mock_dependencies['mock_git_clone'].return_value, 
        branch="commit123"
    )

    # Assertions for install_tool_versions call
    mock_dependencies['mock_install_tool_versions'].assert_called_once_with(
        file=override['tool_versions_file']
    )

    # Assertions for set_netrc call
    mock_dependencies['mock_set_netrc'].assert_called_once_with(
        password="token123", 
        machine=override['machine'], 
        login=override['login']
    )

    # Assertions for copy_files_and_dirs call
    expected_source_dir = f"/path/repo-suffix/infra"
    expected_dest_dir = f"/path/repo/infra"
    mock_dependencies['mock_copy_files_and_dirs'].assert_called_once_with(
        source_dir=expected_source_dir.strip(), 
        destination_dir=expected_dest_dir.strip()
    )

    # Assertions for os.chdir to the execution directory
    expected_exec_dir = f"/path/repo/infra"
    mock_dependencies['mock_chdir'].assert_called_with(expected_exec_dir)


def test_with_skip_git_and_repo_exists(mock_dependencies):
    repository_url = "https://github.com/example/repo.git"
    aws_provider_config = MagicMock(
        provider='aws', 
        aws=MagicMock(role_to_assume='role', region='region')
    )
    override = {
        'properties_suffix': 'suffix', 
        'tool_versions_file': 'file', 
        'machine': 'machine', 
        'login': 'login', 
        'infrastructure_dir': 'infra', 
        'environment_dir': 'env',
        'main_branch': 'main'
    }

    # Mock check_git_changes to return True to avoid triggering the RuntimeError
    mock_dependencies['mock_check_git_changes'].return_value = True

    prepare_for_terragrunt(
        repository_url,
        "token123",
        "commit123",
        "prod",
        aws_provider_config,
        True,  # skip_git
        True,  # is_infrastructure
        "/path",
        override
    )

    # Check that git_clone was not called
    mock_dependencies['mock_git_clone'].assert_not_called()

    # Assertions for git_checkout, install_tool_versions, set_netrc, check_git_changes
    # These are expected to be called similar to the test_without_skip_git

    mock_dependencies['mock_git_checkout'].assert_called_once_with(
        repository=MagicMock(), 
        branch="commit123"
    )
    mock_dependencies['mock_install_tool_versions'].assert_called_once_with(
        file=override['tool_versions_file']
    )
    mock_dependencies['mock_set_netrc'].assert_called_once_with(
        password="token123", 
        machine=override['machine'], 
        login=override['login']
    )

    # Assertions for copy_files_and_dirs and os.chdir as in test_without_skip_git
    expected_source_dir = f"/path/repo-suffix/infra"
    expected_dest_dir = f"/path/repo/infra"
    mock_dependencies['mock_copy_files_and_dirs'].assert_called_once_with(
        source_dir=expected_source_dir.strip(), 
        destination_dir=expected_dest_dir.strip()
    )
    expected_exec_dir = f"/path/repo/infra"
    mock_dependencies['mock_chdir'].assert_called_with(expected_exec_dir)

    # Additional checks for AWS provider
    if aws_provider_config.provider == 'aws':
        mock_dependencies['mock_read_key_value_from_file'].assert_called_once_with(
            f"/path/repo/accounts.json", 
            "prod"
        )
        mock_dependencies['mock_aws_assume_role'].assert_called_once_with(
            aws_provider_config.aws.role_to_assume, 
            "aws_profile",  # This value is returned by the read_key_value_from_file mock
            aws_provider_config.aws.region
        )


def test_with_skip_git_and_repo_not_exists(mocker):
    mocker.patch('os.path.exists', return_value=False)
    
    repository_url = "https://github.com/example/repo.git"
    override = {
        'properties_suffix': 'suffix', 
        'tool_versions_file': 'file', 
        'machine': 'machine', 
        'login': 'login', 
        'infrastructure_dir': 'infra', 
        'environment_dir': 'env'
    }

    with pytest.raises(RuntimeError, match="Cannot find git repository directories"):
        prepare_for_terragrunt(
            repository_url,
            "token123",
            "commit123",
            "prod",
            MagicMock(provider='aws'),
            True,  # skip_git
            True,  # is_infrastructure
            "/path",
            override
        )

    # Assertions to confirm no further actions were taken
    mocker.patch('launch.pipeline.common.functions.git_clone').assert_not_called()
    mocker.patch('launch.pipeline.common.functions.git_checkout').assert_not_called()
    mocker.patch('launch.pipeline.common.functions.install_tool_versions').assert_not_called()
    mocker.patch('launch.pipeline.common.functions.set_netrc').assert_not_called()
    mocker.patch('launch.pipeline.common.functions.check_git_changes').assert_not_called()
    mocker.patch('launch.pipeline.common.functions.copy_files_and_dirs').assert_not_called()
    mocker.patch('launch.pipeline.common.functions.read_key_value_from_file').assert_not_called()
    mocker.patch('launch.pipeline.provider.aws.functions.assume_role').assert_not_called()

    # Optionally, check that os.chdir was not called or was called only up to a certain point
    mocker.patch('os.chdir').assert_not_called() 


def test_aws_provider_config(mock_dependencies, mocker):
    repository_url = "https://github.com/example/repo.git"
    override = {
        'properties_suffix': 'suffix', 
        'tool_versions_file': 'file', 
        'machine': 'machine', 
        'login': 'login', 
        'infrastructure_dir': 'infra', 
        'environment_dir': 'env',
        'main_branch': 'main'
    }
    provider_config = MagicMock(provider='aws', aws=MagicMock(role_to_assume='role', region='region'))

    # Mock check_git_changes to return True to avoid triggering the RuntimeError
    mock_dependencies['mock_check_git_changes'].return_value = True

    prepare_for_terragrunt(
        repository_url,
        "token123",
        "commit123",
        "prod",
        provider_config,
        False,  # skip_git
        True,   # is_infrastructure
        "/path",
        override
    )

    # Assertions for git operations
    mock_dependencies['mock_git_clone'].assert_any_call(
        target_dir="repo",
        clone_url=repository_url
    )

    # Assertions for install_tool_versions and set_netrc
    mock_dependencies['mock_install_tool_versions'].assert_called_once_with(
        file=override['tool_versions_file']
    )
    mock_dependencies['mock_set_netrc'].assert_called_once_with(
        password="token123", 
        machine=override['machine'], 
        login=override['login']
    )

    # Assertions for check_git_changes
    mock_dependencies['mock_check_git_changes'].assert_called_once_with(
        repository=mock_dependencies['mock_git_clone'].return_value,
        commit_id="commit123", 
        main_branch=override['main_branch'], 
        directory=override['infrastructure_dir']
    )

    # Assertions for file copying
    expected_source_dir = f"/path/repo-suffix/infra"
    expected_dest_dir = f"/path/repo/infra"
    mock_dependencies['mock_copy_files_and_dirs'].assert_called_once_with(
        source_dir=expected_source_dir.strip(), 
        destination_dir=expected_dest_dir.strip()
    )

    # Assertions for AWS role assumption
    mock_dependencies['mock_read_key_value_from_file'].assert_called_once_with(
        f"/path/repo/accounts.json", 
        "prod"
    )
    mock_dependencies['mock_aws_assume_role'].assert_called_once_with(
        'role', 
        'aws_profile', 
        'region'
    )


def test_no_infra_folder_with_is_infrastructure(mock_dependencies):
    repository_url = "https://github.com/example/repo.git"
    override = {
        'properties_suffix': 'suffix', 
        'tool_versions_file': 'file', 
        'machine': 'machine', 
        'login': 'login', 
        'infrastructure_dir': 'infra', 
        'environment_dir': 'env',
        'main_branch': 'main'
    }

    # Mock check_git_changes to return False to simulate no git differences
    mock_dependencies['mock_check_git_changes'].return_value = False

    with pytest.raises(RuntimeError, match="No  infra folder, however, is_infrastructure: True"):
        prepare_for_terragrunt(
            repository_url,
            "token123",
            "commit123",
            "prod",
            MagicMock(provider='aws'),
            False,  # skip_git
            True,   # is_infrastructure
            "/path",
            override
        )

    # Here, you can also add assertions to verify that no further actions were taken after the error was raised

def test_error_when_no_git_diff_and_is_infrastructure(mock_dependencies):
    repository_url = "https://github.com/example/repo.git"
    override = {
        'properties_suffix': 'suffix', 
        'tool_versions_file': 'file', 
        'machine': 'machine', 
        'login': 'login', 
        'infrastructure_dir': 'infra', 
        'environment_dir': 'env',
        'main_branch': 'main'
    }

    # Simulate no git differences
    mock_dependencies['mock_check_git_changes'].return_value = False

    with pytest.raises(RuntimeError, match="No  infra folder, however, is_infrastructure: True"):
        prepare_for_terragrunt(
            repository_url,
            "token123",
            "commit123",
            "prod",
            MagicMock(provider='aws'),
            False,  # skip_git
            True,   # is_infrastructure
            "/path",
            override
        )


def test_error_when_skip_git_and_repo_not_defined(mock_dependencies, mocker):
    repository_url = "https://github.com/example/repo.git"
    override = {
        'properties_suffix': 'suffix', 
        'tool_versions_file': 'file', 
        'machine': 'machine', 
        'login': 'login', 
        'infrastructure_dir': 'infra', 
        'environment_dir': 'env',
        'main_branch': 'main'
    }

    # Ensure that git_clone is not called and does not set the repository
    mock_dependencies['mock_git_clone'].return_value = None

    with pytest.raises(UnboundLocalError):
        prepare_for_terragrunt(
            repository_url,
            "token123",
            "commit123",
            "prod",
            MagicMock(provider='aws'),
            True,  # skip_git
            True,   # is_infrastructure
            "/path",
            override
        )
