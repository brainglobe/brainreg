import os
import platform
from pathlib import Path
from typing import Optional

__os_folder_names = {"Linux": "linux_x64", "Darwin": "osX", "Windows": "win64"}

try:
    os_system_name = platform.system()
    os_folder_name = __os_folder_names[os_system_name]
except KeyError:
    raise ValueError(
        f"Platform {platform.system()} is not recognised as a valid platform. "
        f"Valid platforms are : {__os_folder_names.keys()}"
    )

_IS_WINDOWS_OS = os_system_name == "Windows"

packaged_binaries_folder = (
    Path(__file__).parent.parent.parent / "bin" / "nifty_reg"
)


def conda_niftyreg_path() -> Optional[Path]:
    """
    If a conda install of niftyreg is available, return the directory
    containing the niftyreg binaries.
    """
    if "CONDA_PREFIX" in os.environ:
        conda_prefix = Path(os.environ["CONDA_PREFIX"])

        if platform.system() == "Windows":
            # Install prefix into conda environments on Windows
            # is CONDA_PREFIX / Library / bin
            bin_path = conda_prefix / "Library" / "bin"

            # Determine if the binaries are present
            # Binaries MUST have .exe appended to them in this case
            if (bin_path / "reg_aladin.exe").exists():
                return bin_path
        else:
            # On MacOS and Linux, binaries are placed into
            # CONDA_PREFIX / bin
            bin_path = conda_prefix / "bin"

            # Determine if the binaries are present
            if (bin_path / "reg_aladin").exists():
                return bin_path
    # If the binaries are not installed into the conda environment,
    # or there is no conda environment, return None as a fail-case
    return None


_CONDA_NIFTYREG_BINARY_PATH = conda_niftyreg_path()


def get_binary(program_name: str) -> Path:
    """
    Get path to one of the niftyreg binaries.

    If niftyreg is installed via conda, use those binaries, otherwise fall
    back on bundled binaries.
    """
    if _CONDA_NIFTYREG_BINARY_PATH is not None:
        bin_path = _CONDA_NIFTYREG_BINARY_PATH / program_name
    else:
        bin_path = packaged_binaries_folder / os_folder_name / program_name

    # Append exe label to Windows executables
    # It looks like subprocess is actually able to cope without the .exe
    # appended, but just to be safe we'll include it on Windows OS calls
    if _IS_WINDOWS_OS:
        bin_path = bin_path.parent / f"{bin_path.stem}.exe"
    return bin_path
