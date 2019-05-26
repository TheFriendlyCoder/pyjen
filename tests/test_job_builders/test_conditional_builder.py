import pytest
from pyjen.jenkins import Jenkins
from pyjen.plugins.conditionalbuilder import ConditionalBuilder
from pyjen.plugins.runcondition_always import AlwaysRun
from pyjen.plugins.runcondition_never import NeverRun
from pyjen.plugins.runcondition_and import AndCondition
from pyjen.plugins.runcondition_not import NotCondition
from pyjen.plugins.shellbuilder import ShellBuilder
from pyjen.plugins.freestylejob import FreestyleJob
from ..utils import async_assert, clean_job, assert_elements_equal


def test_add_conditional_builder(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    expected_job_name = "test_add_conditional_builder"
    jb = jk.create_job(expected_job_name, FreestyleJob)
    with clean_job(jb):
        expected_output = "Here is my sample output..."
        expected_cmd = "echo " + expected_output
        shell_builder = ShellBuilder.create(expected_cmd)
        condition = AlwaysRun.create()
        conditional_builder = ConditionalBuilder.create(condition, shell_builder)
        jb.add_builder(conditional_builder)

        # Get a fresh copy of our job to ensure we have an up to date
        # copy of the config.xml for the job
        async_assert(lambda: jk.find_job(expected_job_name).builders)

        builders = jk.find_job(expected_job_name).builders

        # Make sure the builder was successfully added and it's response
        # data can be parsed correctly
        assert isinstance(builders, list)
        assert len(builders) == 1
        assert isinstance(builders[0], ConditionalBuilder)
        assert builders[0].builder is not None
        assert isinstance(builders[0].builder, ShellBuilder)
        assert builders[0].builder.script == expected_cmd
        assert_elements_equal(builders[0].builder.node, shell_builder.node)


def test_always_run_condition(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    expected_job_name = "test_always_run_condition"
    jb = jk.create_job(expected_job_name, FreestyleJob)
    with clean_job(jb):
        expected_output = "Here is my sample output..."
        expected_cmd = "echo " + expected_output
        shell_builder = ShellBuilder.create(expected_cmd)
        condition = AlwaysRun.create()
        conditional_builder = ConditionalBuilder.create(condition, shell_builder)
        jb.add_builder(conditional_builder)

        # Wait until our job config has been applied successfully
        async_assert(lambda: jk.find_job(expected_job_name).builders)

        # Make sure the condition is loaded correctly
        builders = jk.find_job(expected_job_name).builders
        assert isinstance(builders[0].condition, AlwaysRun)
        assert  builders[0].condition.get_friendly_name() == "always"

        # Run a build and make sure the build operation actually executed
        jb.start_build()
        async_assert(lambda: jb.last_build)

        assert expected_output in jb.last_build.console_output


def test_never_run_condition(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    expected_job_name = "test_never_run_condition"
    jb = jk.create_job(expected_job_name, FreestyleJob)
    with clean_job(jb):
        expected_output = "Here is my sample output..."
        shell_builder = ShellBuilder.create("echo " + expected_output)
        condition = NeverRun.create()
        conditional_builder = ConditionalBuilder.create(condition, shell_builder)
        jb.add_builder(conditional_builder)

        # Get a fresh copy of our job to ensure we have an up to date
        # copy of the config.xml for the job
        async_assert(lambda: jk.find_job(expected_job_name).builders)

        builders = jk.find_job(expected_job_name).builders

        # Make sure the builder was correctly configured
        assert builders[0].condition is not None
        assert isinstance(builders[0].condition, NeverRun)
        assert builders[0].condition.get_friendly_name() == "never"

        # Finally, just to be sure our build actually did something relevant
        # we make sure the output from our shell command appears in the
        # build output for a build (ie: to ensure the conditional build step
        # actually ran)
        jb.start_build()
        async_assert(lambda: jb.last_build)

        assert expected_output not in jb.last_build.console_output


def test_and_build_condition_true(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    expected_job_name = "test_and_build_condition_true"
    jb = jk.create_job(expected_job_name, FreestyleJob)
    with clean_job(jb):
        expected_output = "Here is my sample output..."
        shell_builder = ShellBuilder.create("echo " + expected_output)
        condition1 = AlwaysRun.create()
        condition2 = AlwaysRun.create()
        condition = AndCondition.create([condition1, condition2])
        conditional_builder = ConditionalBuilder.create(condition, shell_builder)
        jb.add_builder(conditional_builder)

        # Get a fresh copy of our job to ensure we have an up to date
        # copy of the config.xml for the job
        async_assert(lambda: jk.find_job(expected_job_name).builders)

        builders = jk.find_job(expected_job_name).builders

        # Make sure the builder was correctly configured
        assert builders[0].condition is not None
        assert isinstance(builders[0].condition, AndCondition)
        assert builders[0].condition.get_friendly_name() == "and"

        # Finally, just to be sure our build actually did something relevant
        # we make sure the output from our shell command appears in the
        # build output for a build (ie: to ensure the conditional build step
        # actually ran)
        jb.start_build()
        async_assert(lambda: jb.last_build)

        assert expected_output in jb.last_build.console_output


def test_and_build_condition_false(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    expected_job_name = "test_and_build_condition_false"
    jb = jk.create_job(expected_job_name, FreestyleJob)
    with clean_job(jb):
        expected_output = "Here is my sample output..."
        shell_builder = ShellBuilder.create("echo " + expected_output)
        condition1 = AlwaysRun.create()
        condition2 = NeverRun.create()
        condition = AndCondition.create([condition1, condition2])
        conditional_builder = ConditionalBuilder.create(condition, shell_builder)
        jb.add_builder(conditional_builder)

        # Get a fresh copy of our job to ensure we have an up to date
        # copy of the config.xml for the job
        async_assert(lambda: jk.find_job(expected_job_name).builders)

        builders = jk.find_job(expected_job_name).builders

        # Make sure the builder was correctly configured
        assert builders[0].condition is not None
        assert isinstance(builders[0].condition, AndCondition)
        assert builders[0].condition.get_friendly_name() == "and"

        # Finally, just to be sure our build actually did something relevant
        # we make sure the output from our shell command appears in the
        # build output for a build (ie: to ensure the conditional build step
        # actually ran)
        jb.start_build()
        async_assert(lambda: jb.last_build)

        assert expected_output not in jb.last_build.console_output


def test_not_build_condition_true(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    expected_job_name = "test_not_build_condition_true"
    jb = jk.create_job(expected_job_name, FreestyleJob)
    with clean_job(jb):
        expected_output = "Here is my sample output..."
        shell_builder = ShellBuilder.create("echo " + expected_output)
        nested_condition = NeverRun.create()
        condition = NotCondition.create(nested_condition)
        conditional_builder = ConditionalBuilder.create(condition, shell_builder)
        jb.add_builder(conditional_builder)

        # Get a fresh copy of our job to ensure we have an up to date
        # copy of the config.xml for the job
        async_assert(lambda: jk.find_job(expected_job_name).builders)

        builders = jk.find_job(expected_job_name).builders

        # Make sure the builder was correctly configured
        assert builders[0].condition is not None
        assert isinstance(builders[0].condition, NotCondition)
        assert builders[0].condition.get_friendly_name() == "not"

        # Finally, just to be sure our build actually did something relevant
        # we make sure the output from our shell command appears in the
        # build output for a build (ie: to ensure the conditional build step
        # actually ran)
        jb.start_build()
        async_assert(lambda: jb.last_build)

        assert expected_output in jb.last_build.console_output


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
