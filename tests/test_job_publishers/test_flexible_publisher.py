import pytest
from pyjen.plugins.runcondition_always import AlwaysRun
from pyjen.plugins.flexiblepublish import FlexiblePublisher, ConditionalAction
from pyjen.plugins.artifactarchiver import ArtifactArchiverPublisher
from pyjen.plugins.freestylejob import FreestyleJob
from ..utils import async_assert, clean_job


@pytest.mark.vcr()
def test_basic_publisher(jenkins_api):
    upstream_name = "test_basic_publisher"
    jb = jenkins_api.create_job(upstream_name, FreestyleJob)
    with clean_job(jb):
        expected_regex = "*.log"
        new_condition = AlwaysRun.instantiate()
        new_pub = ArtifactArchiverPublisher.instantiate(expected_regex)
        new_action = ConditionalAction.instantiate(new_condition, [new_pub])
        pub = FlexiblePublisher.instantiate([new_action])
        jb.add_publisher(pub)

        # Get a fresh copy of our job to ensure we have an up to date
        # copy of the config.xml for the job
        async_assert(lambda: jenkins_api.find_job(upstream_name).publishers)
        pubs = jenkins_api.find_job(upstream_name).publishers

        assert isinstance(pubs, list)
        assert len(pubs) == 1
        cur_pub = pubs[0]
        assert isinstance(cur_pub, FlexiblePublisher)
        assert isinstance(cur_pub.actions, list)
        assert len(cur_pub.actions) == 1
        cur_action = cur_pub.actions[0]
        assert isinstance(cur_action, ConditionalAction)
        assert isinstance(cur_action.publishers, list)
        assert len(cur_action.publishers) == 1
        cur_nested_pub = cur_action.publishers[0]
        assert isinstance(cur_nested_pub, ArtifactArchiverPublisher)
        assert cur_nested_pub.artifact_regex == expected_regex
