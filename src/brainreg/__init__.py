from importlib.metadata import PackageNotFoundError, version
from . import *

try:
    __version__ = version("brainreg")
except PackageNotFoundError:
    # package is not installed
    pass

__author__ = "Adam Tyson"
