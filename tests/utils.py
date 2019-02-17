"""helper functions used by the tests"""
import os
import glob


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

