import os
from pathlib import Path
from typing import Tuple

from brainreg.backend.niftyreg.niftyreg_binaries import (
    _CONDA_NIFTYREG_BINARY_PATH,
    get_binary,
    packaged_binaries_folder,
)


def packaged_binaries_are_used() -> Tuple[bool, Path]:
    """
    Return a (bool, Path) tuple which has the values:
        boolean:
            TRUE if the get_binary function points to one of the niftyreg binaries
             that are included with the package.
            FALSE otherwise.
        Path:
            The path to the folder containing the niftyreg binaries that were found
    """
    using_binary = get_binary("reg_aladin")
    return (
        packaged_binaries_folder in using_binary.parents,
        using_binary.parent,
    )


def test_conda_with_niftyreg():
    """
    Check the following:
    - If we are not in a conda environment, the packaged niftyreg binaries are used by the backend
    - If we are in a conda environment and niftyreg is not conda-installed, the packaged niftyreg binaries are used by the backend
    - If we are in a conda environment and niftyreg IS conda-installed, the conda-installed binaries are used by the backend.
    """
    if "CONDA_PREFIX" not in os.environ:
        # We are not in a conda envrionment
        # _CONDA_NIFTYREG_BINARY_PATH should be none
        assert (
            _CONDA_NIFTYREG_BINARY_PATH is None
        ), f"Not in a conda environment but _CONDA_NIFTYREG_BINARY_PATH is non-None: {_CONDA_NIFTYREG_BINARY_PATH}"

        using_packaged_binaries, bin_folder = packaged_binaries_are_used()
        assert (
            using_packaged_binaries
        ), f"There is no CONDA_PREFIX, but non-packaged binaries in {bin_folder} are being used!"
    else:
        # We are in a conda environment.
        # Either this environment does not have niftyreg installed, or it does.
        if _CONDA_NIFTYREG_BINARY_PATH is None:
            # Apparently niftyreg is not installed in this environment
            # Assert the located binaries are the packaged ones
            using_packaged_binaries, bin_folder = packaged_binaries_are_used()
            assert using_packaged_binaries, f"Conda environment without niftyreg installed exists, but non-packaged binaries in {bin_folder} are being used."
        else:
            # We are in a conda environment that _has_ niftyreg conda-installed
            # Assert that we are using the CONDA-installed binaries
            using_packaged_binaries, bin_folder = packaged_binaries_are_used()
            assert not using_packaged_binaries, f"Packaged binaries are being used despite appearing to be installed by CONDA at {_CONDA_NIFTYREG_BINARY_PATH}"
