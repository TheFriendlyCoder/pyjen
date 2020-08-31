from pyjen.plugins.buildtriggerpublisher import BuildTriggerPublisher
from pyjen.plugins.freestylejob import FreestyleJob
from ..utils import async_assert, clean_job


def test_add_build_trigger_publisher(jenkins_api):
    upstream_name = "test_add_build_trigger_publisher1"
    jb = jenkins_api.create_job(upstream_name, FreestyleJob)
    with clean_job(jb):
        downstream_name = "test_add_build_trigger_publisher2"
        jb2 = jenkins_api.create_job(downstream_name, FreestyleJob)
        with clean_job(jb2):
            publisher = BuildTriggerPublisher.instantiate([downstream_name])
            jb.add_publisher(publisher)

            # Get a fresh copy of our job to ensure we have an up to date
            # copy of the config.xml for the job
            async_assert(lambda: jenkins_api.find_job(upstream_name).publishers)
            pubs = jenkins_api.find_job(upstream_name).publishers

            assert isinstance(pubs, list)
            assert len(pubs) == 1
            assert isinstance(pubs[0], BuildTriggerPublisher)
            names = pubs[0].job_names
            assert isinstance(names, list)
            assert len(names) == 1
            assert names[0] == downstream_name


def test_one_downstream_job(jenkins_api):
    jb = jenkins_api.create_job("test_one_downstream_job1", FreestyleJob)
    with clean_job(jb):
        expected_name = "test_one_downstream_job2"
        jb2 = jenkins_api.create_job(expected_name, FreestyleJob)
        with clean_job(jb2):
            publisher = BuildTriggerPublisher.instantiate([expected_name])
            jb.add_publisher(publisher)

            async_assert(lambda: jb.downstream_jobs)
            res = jb.downstream_jobs

            assert isinstance(res, list)
            assert len(res) == 1
            assert res[0].name == expected_name


def test_multiple_downstream_jobs(jenkins_api):
    jb = jenkins_api.create_job("test_multiple_downstream_jobs1", FreestyleJob)
    with clean_job(jb):
        expected_name1 = "test_multiple_downstream_jobs2"
        jb2 = jenkins_api.create_job(expected_name1, FreestyleJob)
        with clean_job(jb2):
            expected_name2 = "test_multiple_downstream_jobs3"
            jb3 = jenkins_api.create_job(expected_name2, FreestyleJob)
            with clean_job(jb3):
                all_names = [expected_name1,expected_name2]
                publisher = BuildTriggerPublisher.instantiate(all_names)
                jb.add_publisher(publisher)

                async_assert(lambda: jb.downstream_jobs)
                res = jb.downstream_jobs

                assert isinstance(res, list)
                assert len(res) == 2
                assert res[0].name in all_names
                assert res[1].name in all_names


def test_one_upstream_job(jenkins_api):
    parent_job_name = "test_one_upstream_job1"
    jb = jenkins_api.create_job(parent_job_name, FreestyleJob)
    with clean_job(jb):
        child_job_name = "test_one_upstream_job2"
        jb2 = jenkins_api.create_job(child_job_name, FreestyleJob)
        with clean_job(jb2):
            publisher = BuildTriggerPublisher.instantiate([child_job_name])
            jb.add_publisher(publisher)

            async_assert(lambda: jb2.upstream_jobs)
            res = jb2.upstream_jobs

            assert isinstance(res, list)
            assert len(res) == 1
            assert res[0].name == parent_job_name


def test_multiple_upstream_jobs(jenkins_api):
    child_job_name = "test_multiple_upstream_jobs1"
    jb = jenkins_api.create_job(child_job_name, FreestyleJob)
    with clean_job(jb):
        expected_name1 = "test_multiple_upstream_jobs2"
        jb2 = jenkins_api.create_job(expected_name1, FreestyleJob)
        with clean_job(jb2):
            expected_name2 = "test_multiple_upstream_jobs3"
            jb3 = jenkins_api.create_job(expected_name2, FreestyleJob)
            with clean_job(jb3):
                all_names = [expected_name1,expected_name2]
                publisher = BuildTriggerPublisher.instantiate([child_job_name])
                jb2.add_publisher(publisher)
                jb3.add_publisher(publisher)

                async_assert(lambda: len(jb.upstream_jobs) == 2)
                res = jb.upstream_jobs

                assert isinstance(res, list)
                assert len(res) == 2
                assert res[0].name in all_names
                assert res[1].name in all_names
