import os
import sys
from pathlib import Path

import pytest

from brainreg.cli import main as brainreg_run
from brainreg.exceptions import LoadFileException

test_data_dir = Path(os.getcwd()) / "tests" / "data"

one_2d_tiff_data_dir = test_data_dir / "input" / "exceptions" / "one_2d_tiff"
one_3d_tiff_data_dir = test_data_dir / "input" / "exceptions" / "one_2d_tiff"
mismatched_dims_data_dir = (
    test_data_dir / "input" / "exceptions" / "mismatched_dims"
)
test_output = test_data_dir / "test_output"


@pytest.fixture(scope="session")
def test_output_dir(tmp_path_factory):
    test_output_dir = tmp_path_factory.mktemp("output_dir")
    return test_output_dir


def get_default_brainreg_args(data_dir, test_output_dir):
    return [
        "brainreg",
        str(data_dir),
        str(test_output_dir),
        "-v",
        "50",
        "40",
        "50",
        "--orientation",
        "psl",
        "--atlas",
        "allen_mouse_100um",
    ]


def test_mismatched_dims_error(test_output_dir):
    """
    Test case in which images files are not the same dimensions.
    """
    brainreg_args = get_default_brainreg_args(
        mismatched_dims_data_dir, test_output_dir
    )
    sys.argv = brainreg_args

    with pytest.raises(LoadFileException) as e:
        brainreg_run()

    assert (
        f"File at {mismatched_dims_data_dir} "
        f"failed to load. Ensure all image files "
        f"contain the same number of pixels. Full traceback above."
        in e.value.message
    )


def test_one_2d_tiff_error(test_output_dir):
    """
    Test case in which a single 2D image is in the folder,
    which is not supported.
    """
    brainreg_args = get_default_brainreg_args(
        one_2d_tiff_data_dir, test_output_dir
    )
    sys.argv = brainreg_args

    with pytest.raises(LoadFileException) as e:
        brainreg_run()

    assert (
        e.value.message == "Attempted to load directory containing a single "
        "two dimensional .tiff file. Pass a folder "
        "containing 3D tiff file or multiple 2D .tiff files."
    )


def test_one_3d_tiff_error(test_output_dir):
    """
    Test the case in which the dir contains a 3D Tiff that
    should be specified by passing the filename not folder.
    """
    brainreg_args = get_default_brainreg_args(
        one_3d_tiff_data_dir, test_output_dir
    )
    sys.argv = brainreg_args

    with pytest.raises(LoadFileException) as e:
        brainreg_run()

    assert (
        e.value.message == "Attempted to load directory containing a single "
        "two dimensional .tiff file. Pass a folder containing "
        "3D tiff file or multiple 2D .tiff files."
    )
