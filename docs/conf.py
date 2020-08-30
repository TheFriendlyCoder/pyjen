"""
Configuration file for the Sphinx documentation builder.
This file does only contain a selection of the most common options. For a
full list see the documentation:
http://www.sphinx-doc.org/en/stable/config
"""

import ast
import os
import sys
from sphinx.ext.intersphinx import InventoryAdapter

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
_base_path = os.path.abspath(os.path.dirname(__file__))
_src_dir = os.path.abspath(os.path.join(_base_path, '..', 'src'))
sys.path.insert(0, _src_dir)


# -- Project information -----------------------------------------------------

copyright = '2020, Kevin S. Phillips'  # pylint: disable=redefined-builtin
author = 'Kevin S. Phillips'
_proj_props = ast.literal_eval(open('../project.prop').read())
_proj_dir = os.path.join(_src_dir, _proj_props["NAME"])
with open(os.path.join(_proj_dir, "version.py")) as prop_file:
    _data = ast.parse(prop_file.read())
    _proj_props["VERSION"] = _data.body[0].value.s

project = _proj_props["NAME"]
# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.
#
# The short X.Y version.
version = _proj_props["VERSION"]
# The full version, including alpha/beta/rc tags.
release = version

# -- General configuration ---------------------------------------------------
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.intersphinx',
    'sphinx.ext.todo',
    'sphinx.ext.viewcode',
    'sphinxcontrib.apidoc',
    'sphinx.ext.napoleon',
    'sphinx_rtd_theme',
]

templates_path = ['_templates']
source_suffix = '.rst'
master_doc = 'index'
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']
pygments_style = 'sphinx'

# -- Options for apidoc/napoleon extensions ------------------------------------
apidoc_module_dir = _proj_dir
apidoc_output_dir = os.path.join(_base_path, "api")
apidoc_separate_modules = True
napoleon_numpy_docstring = False
autoclass_content = "both"
napoleon_include_special_with_doc = False

# -- Options for HTML output -------------------------------------------------
html_theme = 'sphinx_rtd_theme'
html_theme_options = {
    "style_external_links": True,
}

# -- Options for intersphinx extension ---------------------------------------
intersphinx_mapping = {
    "python": ("https://docs.python.org/", None),
    "requests": ("https://requests.readthedocs.io/en/master/", None),
}

intersphinx_aliases = {
    'py:exception': {
        'requests.HTTPError': 'requests.exceptions.HTTPError'
    }
}


def add_intersphinx_aliases_to_inv(app):
    """Workaround for data type mismatches between intersphinx document sources

    Implementation based on a workaround found here:
    https://github.com/sphinx-doc/sphinx/issues/5603

    The calling code need only define a dictionary that maps the source object
    as it appears in the Sphinx object tree, to the actual location for the
    object definition in an object.inv inventory file. The syntax looks like
    this:
    ::

        intersphinx_aliases = {
            'dt-domain': {
                'src-obj-name': 'target-obj-name'
            }
        }

    TIP: when debugging intersphinx mapping problems, it is helpful to use
    the sphobjinv tool:
        https://pypi.org/project/sphobjinv/

    Example:
    sphobjinv suggest https://requests.readthedocs.io/en/master/ HTTPError -su
    """
    inventories = InventoryAdapter(app.builder.env)

    for domain, mapping in app.config.intersphinx_aliases.items():
        if domain not in inventories.main_inventory:
            raise NotImplementedError(
                "Domain {0} not found in Sphinx inventory".format(domain)
            )
        for source, target in mapping.items():
            if source not in inventories.main_inventory[domain]:
                raise NotImplementedError(
                    "Source object {0} not found in Sphinx domain {1}".format(
                        source, domain
                    )
                )
            inventories.main_inventory[domain][target] = \
                inventories.main_inventory[domain][source]


def setup(app):
    """Custom Sphinx extension manager entry point method"""
    app.add_config_value('intersphinx_aliases', {}, 'env')
    app.connect('builder-inited', add_intersphinx_aliases_to_inv)
