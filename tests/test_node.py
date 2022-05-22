import pytest
from .utils import clean_job, async_assert
from pyjen.plugins.shellbuilder import ShellBuilder
from pyjen.plugins.freestylejob import FreestyleJob


@pytest.mark.vcr()
def test_get_nodes(jenkins_api):
    result = jenkins_api.nodes

    assert result is not None
    assert isinstance(result, list)
    assert len(result) == 1


@pytest.mark.vcr()
def test_find_node(jenkins_api):
    expected_name = "Built-In Node"
    result = jenkins_api.find_node(expected_name)

    assert result is not None
    assert result.name == expected_name


@pytest.mark.vcr()
def test_node_online(jenkins_api):
    node = jenkins_api.nodes[0]

    assert node.is_offline is False


@pytest.mark.vcr()
def test_toggle_offline(jenkins_api):
    node = jenkins_api.nodes[0]

    assert node.is_offline is False
    node.toggle_offline()
    assert node.is_offline is True
    node.toggle_offline()
    assert node.is_offline is False


@pytest.mark.vcr()
def test_toggle_offline_with_message(jenkins_api):
    node = jenkins_api.nodes[0]

    assert node.is_offline is False
    node.toggle_offline("Performing maintenance on node")
    assert node.is_offline is True
    node.toggle_offline()
    assert node.is_offline is False


@pytest.mark.vcr()
def test_is_idle(jenkins_api):
    node = jenkins_api.nodes[0]

    assert node.is_idle is True


@pytest.mark.vcr()
def test_node_busy(jenkins_api):
    node = jenkins_api.nodes[0]
    expected_job_name = "test_node_busy_job"
    jb = jenkins_api.create_job(expected_job_name, FreestyleJob)
    with clean_job(jb):
        jb.quiet_period = 0
        shell_builder = ShellBuilder.instantiate("sleep 2")
        jb.add_builder(shell_builder)

        # Get a fresh copy of our job to ensure we have an up to date
        # copy of the config.xml for the job
        async_assert(lambda: jenkins_api.find_job(expected_job_name).builders)

        # Trigger a build
        jb.start_build()

        # The 'last_build' reference becomes available as soon as the previously
        # triggered build exits the queue and starts running. So we wait for the
        # last build to become valid before checking the node activity
        async_assert(lambda: jb.last_build)

        assert node.is_idle is False

        # Wait until the test build completes
        async_assert(lambda: jb.last_good_build)


@pytest.mark.vcr()
def test_wait_for_idle(jenkins_api):
    node = jenkins_api.nodes[0]
    expected_job_name = "test_wait_for_idle_job"
    jb = jenkins_api.create_job(expected_job_name, FreestyleJob)
    with clean_job(jb):
        jb.quiet_period = 0
        shell_builder = ShellBuilder.instantiate("sleep 2")
        jb.add_builder(shell_builder)

        # Get a fresh copy of our job to ensure we have an up to date
        # copy of the config.xml for the job
        async_assert(lambda: jenkins_api.find_job(expected_job_name).builders)

        # Trigger a build
        jb.start_build()

        # The 'last_build' reference becomes available as soon as the previously
        # triggered build exits the queue and starts running. So we wait for the
        # last build to become valid before checking the node activity
        async_assert(lambda: jb.last_build)

        assert node.is_idle is False
        assert node.wait_for_idle()
        assert node.is_idle


@pytest.mark.vcr()
def test_wait_for_idle_timeout(jenkins_api):
    node = jenkins_api.nodes[0]
    expected_job_name = "test_wait_for_idle_timeout_job"
    jb = jenkins_api.create_job(expected_job_name, FreestyleJob)
    with clean_job(jb):
        jb.quiet_period = 0
        shell_builder = ShellBuilder.instantiate("sleep 5")
        jb.add_builder(shell_builder)

        # Get a fresh copy of our job to ensure we have an up to date
        # copy of the config.xml for the job
        async_assert(lambda: jenkins_api.find_job(expected_job_name).builders)

        # Trigger a build
        jb.start_build()

        # The 'last_build' reference becomes available as soon as the previously
        # triggered build exits the queue and starts running. So we wait for the
        # last build to become valid before checking the node activity
        async_assert(lambda: jb.last_build)

        assert node.is_idle is False
        assert node.wait_for_idle(2) is False

        async_assert(lambda: jb.last_good_build)
