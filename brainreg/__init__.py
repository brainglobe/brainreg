from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("brainreg")
    del version
except PackageNotFoundError:
    # package is not installed
    pass

__author__ = "Adam Tyson"
