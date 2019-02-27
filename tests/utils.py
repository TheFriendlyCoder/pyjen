"""helper functions used by the tests"""
import os
import glob
import time
from contextlib import contextmanager


@contextmanager
def clean_job(jenkins_job):
    """Helper context manager that deletes a Jenkins job even when tests fail

    :param jenkins_job: Jenkins job to manage
    :type jenkins_job: :class:`pyjen.job.Job`
    """
    try:
        yield
    finally:
        jenkins_job.delete()


@contextmanager
def clean_view(jenkins_view):
    """Helper context manager that deletes a Jenkins view even when tests fail

    :param jenkins_view: Jenkins view to manage
    :type jenkins_view: :class:`pyjen.view.View`
    """
    try:
        yield
    finally:
        jenkins_view.delete()


def async_assert(test_func):
    """Runs a test function periodically

    Used to test asynchronous test operations that may take some time to
    complete.

    example: async_test(lambda: job.is_healthy)

    :param test_func:
        lambda function that is expected to return a truthy value for a test
        operation. If the lambda returns a falsey value, this helper will
        sleep briefly before repeating the check. After several failed
        attempts, the helper will assert false. Otherwise control returns
        to the caller.
    """
    for i in range(10):
        if test_func():
            break
        time.sleep(1)
    assert test_func()


def count_plugins():
    """Counts the number of plugin modules in the project folder

    :rtype: :class:`int`
    """
    test_dir = os.path.dirname(__file__)
    workspace_dir = os.path.abspath(os.path.join(test_dir, ".."))
    proj_dir = os.path.join(workspace_dir, 'src', 'pyjen')
    plugin_dir = os.path.join(proj_dir, "plugins")

    assert os.path.exists(plugin_dir)

    modules = glob.glob(os.path.join(plugin_dir, "*.py"))

    assert modules

    retval = 0
    for cur_mod in modules:
        if "__init__" in cur_mod:
            continue
        retval += 1
    return retval


if __name__ == "__main__":
    pass

