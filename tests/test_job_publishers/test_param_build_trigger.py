import pytest
from pyjen.jenkins import Jenkins
from pyjen.plugins.paramtrigger import ParameterizedBuildTrigger
from pyjen.plugins.paramtrigger_currentbuildparams import CurrentBuildParams
from pyjen.plugins.paramtrigger_buildtrigger import BuildTriggerConfig
from pyjen.plugins.freestylejob import FreestyleJob
from ..utils import async_assert, clean_job


def test_param_trigger(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    upstream_name = "test_param_trigger"
    jb = jk.create_job(upstream_name, FreestyleJob)
    with clean_job(jb):
        downstream_name = "sample_job"
        new_trigger = BuildTriggerConfig.create([downstream_name])
        pub = ParameterizedBuildTrigger.create([new_trigger])
        jb.add_publisher(pub)

        # Get a fresh copy of our job to ensure we have an up to date
        # copy of the config.xml for the job
        async_assert(lambda: jk.find_job(upstream_name).publishers)
        pubs = jk.find_job(upstream_name).publishers

        assert isinstance(pubs, list)
        assert len(pubs) == 1
        assert isinstance(pubs[0], ParameterizedBuildTrigger)
        triggers = pubs[0].triggers
        assert isinstance(triggers, list)
        assert len(triggers) == 1
        names = triggers[0].job_names
        assert isinstance(names, list)
        assert len(names) == 1
        assert names[0] == downstream_name
        assert triggers[0].condition == "SUCCESS"


def test_trigger_with_current_build_params(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    upstream_name = "test_trigger_with_current_build_params"
    jb = jk.create_job(upstream_name, FreestyleJob)
    with clean_job(jb):
        downstream_name = "sample_job"
        new_trigger = BuildTriggerConfig.create([downstream_name])
        cur_bld_params = CurrentBuildParams.create()
        new_trigger.add_build_param(cur_bld_params)
        new_pub = ParameterizedBuildTrigger.create([new_trigger])
        jb.add_publisher(new_pub)

        # Get a fresh copy of our job to ensure we have an up to date
        # copy of the config.xml for the job
        async_assert(lambda: jk.find_job(upstream_name).publishers)
        pubs = jk.find_job(upstream_name).publishers

        assert len(pubs) == 1
        cur_pub = pubs[0]
        assert len(cur_pub.triggers) == 1
        cur_trig = cur_pub.triggers[0]
        assert len(cur_trig.build_params) == 1
        cur_param_cfg = cur_trig.build_params[0]

        assert isinstance(cur_param_cfg, CurrentBuildParams)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
