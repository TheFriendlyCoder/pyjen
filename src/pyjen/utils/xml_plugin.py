"""Primitives common to all PyJen plugins that extend Jenkins config.xml"""
import logging
import xml.etree.ElementTree as ElementTree


class XMLPlugin(object):
    """Base class for all PyJen plugins that extend Jenkins config.xml

    Plugins derived from this base class are always instantiated with a
    sub-node within a primitive's config.xml. The particulars of these
    sub-nodes including names, attributes, and children nodes, is unique
    to each Jenkins plugin. However, all such PyJen plugins must extend
    this base class to provide those plugin specific behaviors.

    All derived classes are expected to implement the following public
    interfaces:

    @classmethod
    def create(cls, ...):
        a factory method that takes 0 or more parameters (anything
        necessary to construct an instance of the derived class) and returns
        an instance of the class pre-constructed with relevant XML content. Used
        when adding an instance of the plugin to an existing Jenkins object.

    @staticmethod
    def get_jenkins_plugin_name():
        Helper method that returns a character string representation of the
        Jenkins plugin name the class is associated with. This is typically
        the Java class name of the Jenkins plugin the PyJen plugin is meant
        to work with.

    :param node:
        ElementTree XML node with the decoded XML data associated with a plugin
    :type node: :class:`ElementTree.Element`
    """
    def __init__(self, node):
        self._parent = None
        self._root = node
        self._log = logging.getLogger(self.__module__)

    @property
    def parent(self):
        """Gets the parent XML tree this node belongs to"""
        return self._parent

    @parent.setter
    def parent(self, value):
        """Associates this XML node with an existing XML tree"""
        self._parent = value

    def update(self):
        """Updates parent XML tree when one exists"""
        if self._parent is None:
            return
        self._parent.update()

    def __str__(self):
        """String representation of XML node managed by this class

        :rtype: :class:`str`
        """
        return ElementTree.tostring(self._root, encoding="utf-8")

    def __repr__(self):
        """Serialized representation of the XML node managed by this class

        :rtype: :class:`str`
        """
        return ElementTree.tostring(self._root, encoding="utf-8")

    @property
    def node(self):
        """Gets the encoded XML data associated with this plugin

        :rtype: :class:`ElementTree.Element`
        """
        return self._root


if __name__ == "__main__":  # pylint: no cover
    pass
