import pytest
from pyjen.jenkins import Jenkins
from pyjen.plugins.conditionalbuilder_always import AlwaysRun
from pyjen.plugins.flexiblepublish import FlexiblePublisher, ConditionalAction
from pyjen.plugins.artifactarchiver import ArtifactArchiverPublisher
from pyjen.plugins.freestylejob import FreestyleJob
from ..utils import async_assert, clean_job


def test_basic_publisher(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    upstream_name = "test_basic_publisher"
    jb = jk.create_job(upstream_name, FreestyleJob)
    with clean_job(jb):
        expected_regex = "*.log"
        new_condition = AlwaysRun.create()
        new_pub = ArtifactArchiverPublisher.create(expected_regex)
        new_action = ConditionalAction.create(new_condition, [new_pub])
        pub = FlexiblePublisher.create([new_action])
        jb.add_publisher(pub)

        # Get a fresh copy of our job to ensure we have an up to date
        # copy of the config.xml for the job
        async_assert(lambda: jk.find_job(upstream_name).publishers)
        pubs = jk.find_job(upstream_name).publishers

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


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
