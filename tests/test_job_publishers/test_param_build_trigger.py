import pytest
from pyjen.plugins.paramtrigger import ParameterizedBuildTrigger
from pyjen.plugins.paramtrigger_currentbuildparams import CurrentBuildParams
from pyjen.plugins.paramtrigger_buildtrigger import BuildTriggerConfig
from pyjen.plugins.freestylejob import FreestyleJob
from ..utils import async_assert, clean_job


@pytest.mark.vcr()
def test_param_trigger(jenkins_api):
    upstream_name = "test_param_trigger"
    jb = jenkins_api.create_job(upstream_name, FreestyleJob)
    with clean_job(jb):
        downstream_name = "sample_job"
        new_trigger = BuildTriggerConfig.instantiate([downstream_name])
        pub = ParameterizedBuildTrigger.instantiate([new_trigger])
        jb.add_publisher(pub)

        # Get a fresh copy of our job to ensure we have an up to date
        # copy of the config.xml for the job
        async_assert(lambda: jenkins_api.find_job(upstream_name).publishers)
        pubs = jenkins_api.find_job(upstream_name).publishers

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


@pytest.mark.vcr()
def test_trigger_with_current_build_params(jenkins_api):
    upstream_name = "test_trigger_with_current_build_params"
    jb = jenkins_api.create_job(upstream_name, FreestyleJob)
    with clean_job(jb):
        downstream_name = "sample_job"
        new_trigger = BuildTriggerConfig.instantiate([downstream_name])
        cur_bld_params = CurrentBuildParams.instantiate()
        new_trigger.add_build_param(cur_bld_params)
        new_pub = ParameterizedBuildTrigger.instantiate([new_trigger])
        jb.add_publisher(new_pub)

        # Get a fresh copy of our job to ensure we have an up to date
        # copy of the config.xml for the job
        async_assert(lambda: jenkins_api.find_job(upstream_name).publishers)
        pubs = jenkins_api.find_job(upstream_name).publishers

        assert len(pubs) == 1
        cur_pub = pubs[0]
        assert len(cur_pub.triggers) == 1
        cur_trig = cur_pub.triggers[0]
        assert len(cur_trig.build_params) == 1
        cur_param_cfg = cur_trig.build_params[0]

        assert isinstance(cur_param_cfg, CurrentBuildParams)
