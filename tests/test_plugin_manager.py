import pytest
import os


@pytest.mark.vcr()
def test_get_plugins(jenkins_env, jenkins_api):
    results = jenkins_api.plugin_manager.plugins

    assert results is not None
    assert isinstance(results, list)
    assert len(results) >= len(jenkins_env["plugins"])


@pytest.mark.vcr()
def test_plugin_shortname(jenkins_api):
    results = jenkins_api.plugin_manager.plugins

    assert results[0].short_name is not None
    assert isinstance(results[0].short_name, type(u""))


@pytest.mark.vcr()
def test_plugin_longname(jenkins_api):
    results = jenkins_api.plugin_manager.plugins

    assert results[0].long_name is not None
    assert isinstance(results[0].long_name, type(u""))


@pytest.mark.vcr()
def test_plugin_version(jenkins_api):
    results = jenkins_api.plugin_manager.plugins

    assert results[0].version is not None
    assert isinstance(results[0].version, type(u""))


@pytest.mark.vcr()
def test_plugin_enabled(jenkins_api):
    results = jenkins_api.plugin_manager.plugins

    assert results[0].enabled is not None
    assert isinstance(results[0].enabled, bool)
    assert results[0].enabled is True


@pytest.mark.vcr()
def test_plugin_download_url(jenkins_api):
    results = jenkins_api.plugin_manager.plugins

    assert results[0].download_url is not None
    assert isinstance(results[0].download_url, str)
    assert results[0].download_url.startswith("http://updates.jenkins-ci.org/download/plugins/")
    assert results[0].download_url.endswith(".hpi")


@pytest.mark.vcr()
def test_plugin_latest_download_url(jenkins_api):
    results = jenkins_api.plugin_manager.plugins

    assert results[0].latest_download_url is not None
    assert isinstance(results[0].latest_download_url, str)
    assert results[0].latest_download_url.startswith("http://updates.jenkins-ci.org/latest/")
    assert results[0].latest_download_url.endswith(".hpi")


@pytest.mark.vcr()
def test_plugin_info_url(jenkins_api):
    results = jenkins_api.plugin_manager.plugins

    assert results[0].info_url is not None
    assert isinstance(results[0].info_url, type(u""))


@pytest.mark.vcr()
def test_plugin_required_dependencies(jenkins_api):
    # HACK: There's no easy way for us to tell which plugins may be installed
    #       by the test framework in the future, so we just "assume" that there
    #       will always be at least one that has at least one transitive
    #       dependency. Let's find one.
    plugin = None
    for cur_plugin in jenkins_api.plugin_manager.plugins:
        # initial sanity check: make sure our return type is correct
        assert isinstance(cur_plugin.required_dependencies, list)

        if len(cur_plugin.required_dependencies) > 0:
            plugin = cur_plugin
            break

    # verify object state
    assert plugin is not None
    assert isinstance(plugin.required_dependencies, list)
    assert len(plugin.required_dependencies) > 0
    assert isinstance(plugin.required_dependencies[0], dict)
    assert len(plugin.required_dependencies[0].keys()) == 2
    assert "shortName" in plugin.required_dependencies[0]
    assert "version" in plugin.required_dependencies[0]
    assert isinstance(plugin.required_dependencies[0]["shortName"], type(u""))
    assert isinstance(plugin.required_dependencies[0]["version"], type(u""))


@pytest.mark.vcr()
def test_plugin_no_required_dependencies(jenkins_api):
    # HACK: There's no easy way for us to tell which plugins may be installed
    #       by the test framework in the future, so we just "assume" that there
    #       will always be at least one that has no dependencies in it. Let's
    #       find one.
    plugin = None
    for cur_plugin in jenkins_api.plugin_manager.plugins:
        # initial sanity check: make sure our return type is correct
        assert isinstance(cur_plugin.required_dependencies, list)

        if len(cur_plugin.required_dependencies) == 0:
            plugin = cur_plugin
            break

    # verify object state
    assert plugin is not None
    assert isinstance(plugin.required_dependencies, list)
    assert len(plugin.required_dependencies) == 0


@pytest.mark.vcr()
def test_find_plugin_by_shortname_doesnt_exist(jenkins_api):
    result = jenkins_api.plugin_manager.find_plugin_by_shortname("should_not_see_me_fubar_asdf")

    assert result is None


@pytest.mark.skip(reason="To be fixed")
def test_find_plugin_by_shortname(jenkins_env, jenkins_api):
    # NOTE: For some reason the first plugin in our list of test plugins,
    # "workflow-aggregator", doesn't always show up on the list of installed
    # plugins. To ensure consistent behavior of this test we select the last
    # plugin in our list of test plugins which should be a valid third-party
    # plugin that should always appear in the list of those installed
    plugin_long_name = jenkins_env["plugins"][-1]
    expected_short_name = plugin_long_name.split(":")[0]
    result = jenkins_api.plugin_manager.find_plugin_by_shortname(expected_short_name)

    assert result is not None
    assert result.short_name == expected_short_name


@pytest.mark.vcr()
def test_download_plugin(jenkins_api, tmp_path):
    results = jenkins_api.plugin_manager.plugins

    results[0].download(str(tmp_path))

    assert len(os.listdir(str(tmp_path))) == 1
    filename = os.listdir(str(tmp_path))[0]

    assert filename.endswith(".hpi")
    assert results[0].short_name in filename
    assert results[0].version in filename


@pytest.mark.vcr()
def test_download_plugin_new_folder(jenkins_api, tmp_path):
    results = jenkins_api.plugin_manager.plugins

    sub_dir = "test_download_plugin_new_folder"
    output_dir = os.path.join(str(tmp_path), sub_dir)
    results[0].download(output_dir)

    assert os.path.exists(output_dir)
    assert os.path.isdir(output_dir)
    assert len(os.listdir(str(tmp_path))) == 1
    assert os.listdir(str(tmp_path))[0] == sub_dir
    assert len(os.listdir(output_dir)) == 1

    filename = os.listdir(str(output_dir))[0]
    assert filename.endswith(".hpi")
    assert results[0].short_name in filename
    assert results[0].version in filename


@pytest.mark.vcr()
def test_download_plugin_no_overwrite(jenkins_api, tmp_path):
    results = jenkins_api.plugin_manager.plugins

    results[0].download(str(tmp_path))

    assert len(os.listdir(str(tmp_path))) == 1
    with pytest.raises(Exception):
        results[0].download(str(tmp_path))


@pytest.mark.vcr()
def test_download_plugin_overwrite(jenkins_api, tmp_path):
    results = jenkins_api.plugin_manager.plugins

    results[0].download(str(tmp_path))
    assert len(os.listdir(str(tmp_path))) == 1

    results[0].download(str(tmp_path), overwrite=True)
    assert len(os.listdir(str(tmp_path))) == 1
