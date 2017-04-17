"""Primitives for operating on SCM properties of Jenkins jobs with no source control configuration"""


class NullSCM:
    """SCM plugin for Jobs with no source control configurations"""

    def __init__(self, node):
        """
        :param node: XML node defining the settings for a this plugin
        :type node: :class:`ElementTree.Element`
        """
        self._root = node
        assert 'class' in self._root.attrib
        assert self._root.attrib['class'] == 'hudson.scm.NullSCM'


if __name__ == "__main__":  # pragma: no cover
    pass
