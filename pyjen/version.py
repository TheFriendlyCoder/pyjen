"""PyJen package version"""

pre_release = True
if pre_release:
    _ver_suffix = ".dev0"
else:
    _ver_suffix = ""

# NOTE: We declare the version number here, separately from the other PyJen modules, so that it can be parsed without having
# to import any PyJen modules. This is helpful when using the setup.py script to generate redistributable packages as it is
# safer to not import any modules from the modules you are packaging.  (ie: importing a module may fail if the import depends
# on other modules being installed, which may or may not exist on the system generating the package)
__version__ = "0.0.12" + _ver_suffix