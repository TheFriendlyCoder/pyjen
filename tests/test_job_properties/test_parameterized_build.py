import pytest
from pyjen.plugins.parameterizedbuild import ParameterizedBuild
from pyjen.plugins.parambuild_string import ParameterizedBuildStringParameter
from pyjen.plugins.freestylejob import FreestyleJob
from ..utils import async_assert, clean_job


@pytest.mark.vcr()
def test_add_string_parameter(jenkins_api):
    job_name = "test_add_string_parameter"
    jb = jenkins_api.create_job(job_name, FreestyleJob)
    with clean_job(jb):
        expected_param_name = "param1"
        expected_param_val = "fubar"
        expected_param_desc = "My Description"
        expected_param_trim = False
        str_param = ParameterizedBuildStringParameter.instantiate(
            expected_param_name,
            expected_param_val,
            expected_param_desc,
            expected_param_trim)
        build_params = ParameterizedBuild.instantiate([str_param])
        jb.add_property(build_params)

        # Get a fresh copy of our job to ensure we have an up to date
        # copy of the config.xml for the job
        async_assert(lambda: jenkins_api.find_job(job_name).properties)
        properties = jenkins_api.find_job(job_name).properties

        assert isinstance(properties, list)
        assert len(properties) == 1
        assert isinstance(properties[0], ParameterizedBuild)
        params = properties[0].parameters
        assert isinstance(params, list)
        assert len(params) == 1
        act_param = params[0]
        assert isinstance(act_param, ParameterizedBuildStringParameter)
        assert act_param.name == expected_param_name
        assert act_param.default_value == expected_param_val
        assert act_param.description == expected_param_desc
        assert act_param.trim == expected_param_trim
