"""helper functions used by the tests"""
import os
import glob
import time
from contextlib import contextmanager


@contextmanager
def clean_job(jenkins_job, disable=False):
    """Helper context manager that deletes a Jenkins job even when tests fail

    :param jenkins_job: Jenkins job to manage
    :type jenkins_job: :class:`pyjen.job.Job`
    :param bool disable:
        indicates whether the clean operation should be disabled. Defaults to
        False. When set to True, the entity managed by this context manager
        will be preserved. This is useful for debugging purposes.
    """
    try:
        yield
    finally:
        if not disable:
            jenkins_job.delete()


@contextmanager
def clean_view(jenkins_view, disable=False):
    """Helper context manager that deletes a Jenkins view even when tests fail

    :param jenkins_view: Jenkins view to manage
    :type jenkins_view: :class:`pyjen.view.View`
    :param bool disable:
        indicates whether the clean operation should be disabled. Defaults to
        False. When set to True, the entity managed by this context manager
        will be preserved. This is useful for debugging purposes.
    """
    try:
        yield
    finally:
        if not disable:
            jenkins_view.delete()


def async_assert(test_func, duration=10):
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
    :param int duration:
        number of seconds to wait to see if the operation completes
        Defaults to 10 seconds
    """
    for i in range(duration):
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


def assert_elements_equal(element1, element2):
    """Helper method that compares two XML nodes, recursively

    If the nodes differ in any way an assertion failure will be raised

    :param element1: the first XML node to compare
    :param element2: the second XML node to compare"""
    assert element1.tag == element2.tag
    # Sometimes text elements may be `None`, other times they may be empty
    # strings. Other times still they may be strings with nothing but empty
    # white space. Let's just look for non-white space characters to simplify
    # our test cases
    first = (element1.text or "").strip()
    second = (element2.text or "").strip()
    assert first == second
    assert element1.tail == element2.tail
    assert element1.attrib == element2.attrib
    assert len(element1) == len(element2)
    for child1, child2 in zip(element1, element2):
        assert_elements_equal(child1, child2)


if __name__ == "__main__":
    pass

