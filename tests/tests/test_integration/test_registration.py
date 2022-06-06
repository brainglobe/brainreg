import os
import platform
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from imio.load import load_any

from brainreg.cli import main as brainreg_run

test_data_dir = Path(os.getcwd()) / "tests" / "data"

brain_data_dir = test_data_dir / "brain data"
expected_niftyreg_output_dir = (
    test_data_dir / "registration_output" / platform.system()
)

x_pix = "40"
y_pix = "40"
z_pix = "50"

relative_tolerance = 0.01
absolute_tolerance = 10
check_less_precise_pd = 1


# This will do a single run of brainreg when pytest is run
# The outputs are then tested in a separate test below
@pytest.fixture(scope="session")
def niftyreg_output_path(tmp_path_factory):
    test_output_dir = tmp_path_factory.mktemp("output_dir")
    brainreg_args = [
        "brainreg",
        str(brain_data_dir),
        str(test_output_dir),
        "-v",
        z_pix,
        y_pix,
        x_pix,
        "--orientation",
        "psl",
        "--n-free-cpus",
        "0",
        "--atlas",
        "allen_mouse_100um",
        "-d",
        str(brain_data_dir),
    ]

    sys.argv = brainreg_args
    brainreg_run()
    return test_output_dir


@pytest.mark.parametrize(
    "image",
    [
        "boundaries.tiff",
        "deformation_field_0.tiff",
        "deformation_field_1.tiff",
        "deformation_field_2.tiff",
        "downsampled.tiff",
        "downsampled_brain data.tiff",
        "downsampled_standard.tiff",
        "downsampled_standard_brain data.tiff",
        "registered_atlas.tiff",
        "registered_hemispheres.tiff",
    ],
)
def test_images_output(niftyreg_output_path, image):
    are_images_equal(image, niftyreg_output_path, expected_niftyreg_output_dir)


def test_volumes_output(niftyreg_output_path):
    pd.testing.assert_frame_equal(
        pd.read_csv(os.path.join(niftyreg_output_path, "volumes.csv")),
        pd.read_csv(os.path.join(expected_niftyreg_output_dir, "volumes.csv")),
    )


def are_images_equal(image_name, output_directory, test_output_directory):
    image = load_any(
        os.path.join(output_directory, image_name),
    )
    test_image = load_any(
        os.path.join(test_output_directory, image_name),
    )
    np.testing.assert_allclose(
        image, test_image, rtol=relative_tolerance, atol=absolute_tolerance
    )
