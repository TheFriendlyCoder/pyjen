import pytest
import os
import logging
import json
from pyjen.jenkins import Jenkins


def test_get_plugins(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    results = jk.plugin_manager.plugins

    assert results is not None
    assert isinstance(results, list)
    assert len(results) >= len(jenkins_env["plugins"])


def test_plugin_shortname(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    results = jk.plugin_manager.plugins

    assert results[0].short_name is not None
    assert isinstance(results[0].short_name, type(u""))


def test_plugin_longname(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    results = jk.plugin_manager.plugins

    assert results[0].long_name is not None
    assert isinstance(results[0].long_name, type(u""))


def test_plugin_version(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    results = jk.plugin_manager.plugins

    assert results[0].version is not None
    assert isinstance(results[0].version, type(u""))


def test_plugin_enabled(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    results = jk.plugin_manager.plugins

    assert results[0].enabled is not None
    assert isinstance(results[0].enabled, bool)
    assert results[0].enabled is True


def test_plugin_download_url(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    results = jk.plugin_manager.plugins

    assert results[0].download_url is not None
    assert isinstance(results[0].download_url, str)
    assert results[0].download_url.startswith("http://updates.jenkins-ci.org/download/plugins/")
    assert results[0].download_url.endswith(".hpi")


def test_plugin_latest_download_url(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    results = jk.plugin_manager.plugins

    assert results[0].latest_download_url is not None
    assert isinstance(results[0].latest_download_url, str)
    assert results[0].latest_download_url.startswith("http://updates.jenkins-ci.org/latest/")
    assert results[0].latest_download_url.endswith(".hpi")


def test_plugin_info_url(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    results = jk.plugin_manager.plugins

    assert results[0].info_url is not None
    assert isinstance(results[0].info_url, type(u""))


def test_plugin_required_dependencies(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))

    # HACK: There's no easy way for us to tell which plugins may be installed
    #       by the test framework in the future, so we just "assume" that there
    #       will always be at least one that has at least one transitive
    #       dependency. Let's find one.
    plugin = None
    for cur_plugin in jk.plugin_manager.plugins:
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


def test_plugin_no_required_dependencies(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))

    # HACK: There's no easy way for us to tell which plugins may be installed
    #       by the test framework in the future, so we just "assume" that there
    #       will always be at least one that has no dependencies in it. Let's
    #       find one.
    plugin = None
    for cur_plugin in jk.plugin_manager.plugins:
        # initial sanity check: make sure our return type is correct
        assert isinstance(cur_plugin.required_dependencies, list)

        if len(cur_plugin.required_dependencies) == 0:
            plugin = cur_plugin
            break

    # verify object state
    assert plugin is not None
    assert isinstance(plugin.required_dependencies, list)
    assert len(plugin.required_dependencies) == 0


def test_find_plugin_by_shortname_doesnt_exist(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    result = jk.plugin_manager.find_plugin_by_shortname("should_not_see_me_fubar_asdf")

    assert result is None


def test_find_plugin_by_shortname(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    result = jk.plugin_manager.find_plugin_by_shortname(jenkins_env["plugins"][0].split(":")[0])

    assert result is not None
    assert result.short_name == jenkins_env["plugins"][0].split(":")[0]


def test_download_plugin(jenkins_env, tmp_path):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    results = jk.plugin_manager.plugins

    results[0].download(str(tmp_path))

    assert len(os.listdir(str(tmp_path))) == 1
    filename = os.listdir(str(tmp_path))[0]

    assert filename.endswith(".hpi")
    assert results[0].short_name in filename
    assert results[0].version in filename


def test_download_plugin_new_folder(jenkins_env, tmp_path):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    results = jk.plugin_manager.plugins

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


def test_download_plugin_no_overwrite(jenkins_env, tmp_path):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    results = jk.plugin_manager.plugins

    results[0].download(str(tmp_path))

    assert len(os.listdir(str(tmp_path))) == 1
    with pytest.raises(Exception):
        results[0].download(str(tmp_path))


def test_download_plugin_overwrite(jenkins_env, tmp_path):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    results = jk.plugin_manager.plugins

    results[0].download(str(tmp_path))
    assert len(os.listdir(str(tmp_path))) == 1

    results[0].download(str(tmp_path), overwrite=True)
    assert len(os.listdir(str(tmp_path))) == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
