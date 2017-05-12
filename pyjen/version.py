"""package version"""
import pkg_resources

__version__ = pkg_resources.get_distribution("pyjen").version  # pylint: disable=no-member