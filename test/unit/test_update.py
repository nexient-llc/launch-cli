from semver import Version

from launch import update


def test_check_updates_instance_failure(mocker):
    mocked_get_anonymous_github_instance = mocker.patch.object(
        update,
        "get_anonymous_github_instance",
        side_effect=Exception("Failed to connect to GitHub"),
    )
    mocked_get_repo_semantic_versions = mocker.patch.object(
        update, "get_repo_semantic_versions"
    )
    assert update.check_for_updates() is None
    mocked_get_anonymous_github_instance.assert_called_once()
    # If we encounter a failure in retrieving data from GitHub before the stage where we ask for versions, we shouldn't try to get the available versions
    mocked_get_repo_semantic_versions.assert_not_called()


def test_check_for_updates_repo_failure(mocker):
    class FakeInstance:
        def get_repo(full_name_or_id: str):
            raise Exception("Organization or repository name lookup failure")

    mocked_get_anonymous_github_instance = mocker.patch.object(
        update, "get_anonymous_github_instance", return_value=FakeInstance()
    )
    mocked_get_repo_semantic_versions = mocker.patch.object(
        update, "get_repo_semantic_versions"
    )
    assert update.check_for_updates() is None
    mocked_get_anonymous_github_instance.assert_called_once()
    # If we encounter a failure in retrieving data from GitHub before the stage where we ask for versions, we shouldn't try to get the available versions
    mocked_get_repo_semantic_versions.assert_not_called()


def test_check_for_updates_versions_failure(mocker):
    mocked_get_anonymous_github_instance = mocker.patch.object(
        update, "get_anonymous_github_instance"
    )
    mocked_get_repo_semantic_versions = mocker.patch.object(
        update,
        "get_repo_semantic_versions",
        side_effect=Exception(
            "Something went horribly wrong, this code shouldn't raise"
        ),
    )
    assert update.check_for_updates() is None
    # Successful calls to retrieve the instance, and then to call the get_repo on the instance
    assert len(mocked_get_anonymous_github_instance.mock_calls) == 2
    mocked_get_repo_semantic_versions.assert_called_once()


def test_check_for_updates_passes_prerelease_var(mocker):
    older_version = Version(1, 2, 2)
    current_version = Version(1, 2, 3)
    prerelease_version = Version(1, 2, 4, "prerelease")
    mocker.patch.object(update, "SEMANTIC_VERSION", new=current_version)
    mocker.patch.object(
        update,
        "get_repo_semantic_versions",
        return_value=[older_version, current_version, prerelease_version],
    )
    mocker.patch.object(update, "get_anonymous_github_instance")
    # There are two versions newer than our current, older version, but only the latest should be returned.
    assert update.check_for_updates(include_prerelease=False) == None
    assert update.check_for_updates(include_prerelease=True) == prerelease_version


def test_check_for_updates_no_newer_version(mocker):
    older_version = Version(1, 2, 2)
    current_version = Version(1, 2, 3)
    mocker.patch.object(update, "SEMANTIC_VERSION", new=current_version)
    mocker.patch.object(
        update,
        "get_repo_semantic_versions",
        return_value=[older_version, current_version],
    )
    mocker.patch.object(update, "get_anonymous_github_instance")
    # Since our current version is latest, we expect None to be returned since there is no update to perform.
    assert update.check_for_updates() == None


def test_check_for_updates_one_newer_version(mocker):
    older_version = Version(1, 2, 2)
    current_version = Version(1, 2, 3)
    latest_version = Version(1, 2, 4)
    mocker.patch.object(update, "SEMANTIC_VERSION", new=current_version)
    mocker.patch.object(
        update,
        "get_repo_semantic_versions",
        return_value=[older_version, current_version, latest_version],
    )
    mocker.patch.object(update, "get_anonymous_github_instance")
    assert update.check_for_updates() == latest_version


def test_check_for_updates_newest_version(mocker):
    older_version = Version(1, 2, 2)
    current_version = Version(1, 2, 3)
    latest_version = Version(1, 2, 4)
    mocker.patch.object(update, "SEMANTIC_VERSION", new=older_version)
    mocker.patch.object(
        update,
        "get_repo_semantic_versions",
        return_value=[older_version, current_version, latest_version],
    )
    mocker.patch.object(update, "get_anonymous_github_instance")
    assert update.check_for_updates() == latest_version


def test_latest_version_no_prerelease(mocker):
    older_version = Version(1, 2, 2)
    current_version = Version(1, 2, 3)
    latest_version = Version(1, 2, 4)
    mocker.patch.object(update, "SEMANTIC_VERSION", new=older_version)
    result = update.latest_version(
        versions=[older_version, current_version, latest_version]
    )
    assert result == latest_version


def test_latest_version_no_current_match(mocker):
    older_version = Version(1, 2, 2)
    current_version = Version(1, 2, 3)
    mocker.patch.object(update, "SEMANTIC_VERSION", new=current_version)
    result = update.latest_version(versions=[older_version])
    assert result == None


def test_latest_version_current_is_latest(mocker):
    older_version = Version(1, 2, 2)
    current_version = Version(1, 2, 3)
    mocker.patch.object(update, "SEMANTIC_VERSION", new=current_version)
    result = update.latest_version(versions=[older_version, current_version])
    assert result == None


def test_latest_version_prerelease_ignored_when_include_is_not_set(mocker):
    older_version = Version(1, 2, 2)
    current_version = Version(1, 2, 3)
    current_prerelease = Version(1, 2, 4, "alpha-1")
    mocker.patch.object(update, "SEMANTIC_VERSION", new=current_version)
    result = update.latest_version(
        include_prerelease=False,
        versions=[older_version, current_version, current_prerelease],
    )
    assert result == None


def test_latest_version_current_prerelease_is_not_newer(mocker):
    older_version = Version(1, 2, 2)
    current_version = Version(1, 2, 3)
    current_prerelease = Version(1, 2, 3, "alpha-1")
    mocker.patch.object(update, "SEMANTIC_VERSION", new=current_version)
    result = update.latest_version(
        include_prerelease=True,
        versions=[older_version, current_version, current_prerelease],
    )
    assert result == None


def test_latest_version_later_prerelease_is_not_newer_when_include_not_set(mocker):
    older_version = Version(1, 2, 2)
    current_version = Version(1, 2, 3)
    newer_prerelease = Version(1, 2, 4, "alpha-1")
    mocker.patch.object(update, "SEMANTIC_VERSION", new=current_version)
    result = update.latest_version(
        include_prerelease=False,
        versions=[older_version, current_version, newer_prerelease],
    )
    assert result == None


def test_latest_version_later_prerelease_is_newer_when_include_set(mocker):
    older_version = Version(1, 2, 2)
    current_version = Version(1, 2, 3)
    newer_prerelease = Version(1, 2, 4, "alpha-1")
    mocker.patch.object(update, "SEMANTIC_VERSION", new=current_version)
    result = update.latest_version(
        include_prerelease=True,
        versions=[older_version, current_version, newer_prerelease],
    )
    assert result == newer_prerelease
