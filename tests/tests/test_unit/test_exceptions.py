import sys
from pathlib import Path

import pytest

from brainreg.cli import main as brainreg_run
from brainreg.exceptions import LoadFileException

test_data_dir = Path(__file__).parent.parent.parent / "data"
one_tiff_data_dir = test_data_dir / "input" / "exceptions" / "one_tiff"
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
        "File failed to load with "
        "imio. Ensure all image files contain the "
        "same number of pixels. Full traceback above." in e.value.message
    )


def test_one_tiff_data_dir(test_output_dir):
    """
    Test case in which a single 2D image is in the folder,
    which is not supported.

    Some tiffs load as a zero-size array, wheras others
    load as a 2D array (well, 3D array with a singleton).
    Test both cases here.
    """
    brainreg_args = get_default_brainreg_args(
        one_tiff_data_dir, test_output_dir
    )

    sys.argv = brainreg_args

    with pytest.raises(LoadFileException) as e:
        brainreg_run()

    assert (
        e.value.message == "Attempted to load directory containing "
        "a single .tiff file. If the .tiff file "
        "is 3D please pass the full path with "
        "filename. Single 2D .tiff file input is "
        "not supported."
    )
