import os
import platform
from pathlib import Path
from typing import Optional

from pkg_resources import resource_filename

__os_folder_names = {"Linux": "linux_x64", "Darwin": "osX", "Windows": "win64"}

try:
    os_folder_name = __os_folder_names[platform.system()]
except KeyError:
    raise ValueError(
        f"Platform {platform.system()} is not recognised as a valid platform. "
        f"Valid platforms are : {__os_folder_names.keys()}"
    )


def conda_install_path() -> Optional[Path]:
    """
    If a conda install of niftyreg is available, return the directory
    containing the niftyreg binaries.
    """
    if "CONDA_PREFIX" not in os.environ:
        return None

    bin_path = Path(os.environ["CONDA_PREFIX"]) / "bin"
    if (bin_path / "reg_aladin").exists():
        return bin_path

    return None


_CONDA_INSTALL_PATH = conda_install_path()


def get_binary(program_name: str) -> Path:
    """
    Get path to one of the niftyreg binaries.

    If niftyreg is installed via conda, use those binaries, otherwise fall
    back on bundled binaries.
    """
    if _CONDA_INSTALL_PATH is not None:
        return _CONDA_INSTALL_PATH / program_name
    else:
        binaries_folder = resource_filename("brainreg", "bin/nifty_reg")
        return Path(binaries_folder) / os_folder_name / program_name
