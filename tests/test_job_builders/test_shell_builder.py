import pytest
from pyjen.jenkins import Jenkins
from pyjen.plugins.shellbuilder import ShellBuilder
from ..utils import async_assert, clean_job


def test_add_simple_shell_builder(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    job_name = "test_add_simple_shell_builder"
    jb = jk.create_job(job_name, "project")
    with clean_job(jb):
        expected_script = "echo hello"
        shell_builder = ShellBuilder.create(expected_script)
        jb.add_builder(shell_builder)

        # Get a fresh copy of our job to ensure we have an up to date
        # copy of the config.xml for the job
        async_assert(lambda: jk.find_job(job_name).builders)
        builders = jk.find_job(job_name).builders

        assert isinstance(builders, list)
        assert len(builders) == 1
        assert isinstance(builders[0], ShellBuilder)
        assert builders[0].script == expected_script
        assert builders[0].unstable_return_code is None


def test_unstable_return_code(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    job_name = "test_unstable_return_code"
    jb = jk.create_job(job_name, "project")
    with clean_job(jb):
        rcode = 12
        failing_step = ShellBuilder.create("exit " + str(rcode))
        failing_step.unstable_return_code = rcode
        jb.add_builder(failing_step)
        async_assert(lambda: jb.builders)

        # Get a fresh copy of our job to ensure we have an up to date
        # copy of the config.xml for the job
        async_assert(lambda: jk.find_job(job_name).builders)
        builders = jk.find_job(job_name).builders

        assert isinstance(builders, list)
        assert len(builders) == 1
        assert builders[0].unstable_return_code == rcode


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
