"""Primitives common to all PyJen plugins that extend Jenkins config.xml"""
import logging
import xml.etree.ElementTree as ElementTree


class XMLPlugin:
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
    """
    def __init__(self, node):
        """
        Args:
            node (xml.etree.ElementTree.Element):
                XML node with the decoded XML data associated with a plugin
        """
        self._parent = None
        self._root = node
        self._log = logging.getLogger(self.__module__)

    @property
    def parent(self):
        """XMLPlugin: Object that manages an outer XML code block containing
        the nodes managed by this object."""
        return self._parent

    @parent.setter
    def parent(self, value):
        self._parent = value

    def update(self):
        """Updates parent XML tree when one exists"""
        if self._parent is None:
            return
        self._parent.update()

    def __str__(self):
        return ElementTree.tostring(self._root, encoding="utf-8")

    def __repr__(self):
        return ElementTree.tostring(self._root, encoding="utf-8")

    @property
    def node(self):
        """xml.etree.ElementTree.Element: the encoded XML data associated with
        this plugin"""
        return self._root


if __name__ == "__main__":  # pragma: no cover
    pass
