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


def test_get_git_client_plugin(jenkins_env):
    # Integration test to make sure every field for one specific plugin
    # has the correct information in it

    # Expected data loaded from the repr() of the git-client Plugin object
    expected_data = {
        "active": True,
        "backupVersion": None,
        "bundled": False,
        "deleted": False,
        "dependencies": [
            {
                "optional": False,
                "shortName": "apache-httpcomponents-client-4-api",
                "version": "4.5.3-2.0"
            },
            {
                "optional": False,
                "shortName": "credentials",
                "version": "2.1.13"
            },
            {
                "optional": False,
                "shortName": "jsch",
                "version": "0.1.54.1"
            },
            {
                "optional": False,
                "shortName": "ssh-credentials",
                "version": "1.13"
            },
            {
                "optional": False,
                "shortName": "structs",
                "version": "1.9"
            }
        ],
        "downgradable": False,
        "enabled": True,
        "hasUpdate": False,
        "longName": "Jenkins Git client plugin",
        "pinned": False,
        "requiredCoreVersion": "1.625.3",
        "shortName": "git-client",
        "supportsDynamicLoad": "MAYBE",
        "url": "https://wiki.jenkins.io/display/JENKINS/Git+Client+Plugin",
        "version": "2.7.6"
    }
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    result = jk.plugin_manager.find_plugin_by_shortname("git-client")

    assert result is not None
    assert result.short_name == "git-client"

    # dump a copy of our json to the log output so we can easily regenerate
    # new sample data if this test breaks in the future
    logging.debug("New Data:")
    logging.debug(result)

    assert result.long_name == expected_data["longName"]
    assert result.version == expected_data["version"]
    assert result.enabled == expected_data["enabled"]
    assert result.info_url == expected_data["url"]
    assert len(result.required_dependencies) == len(expected_data["dependencies"])

    dep_short_names = [i["shortName"] for i in expected_data["dependencies"]]
    dep_versions = [i["version"] for i in expected_data["dependencies"]]

    for cur_dep in result.required_dependencies:
        assert cur_dep["shortName"] in dep_short_names
        assert cur_dep["version"] in dep_versions

    # final sanity check, to look for newly introduced fields
    assert json.loads(repr(result)) == expected_data


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
