import os
import sys
import platform
import numpy as np
import pandas as pd
from pathlib import Path

from imio.load import load_any

from brainreg.cli import main as brainreg_run

data_dir = Path(__file__).parent.parent.parent / "data" / "brain data"
test_niftyreg_output = data_dir.parent / "registration_output"

x_pix = "40"
y_pix = "40"
z_pix = "50"

relative_tolerance = 0.01
absolute_tolerance = 10
check_less_precise_pd = 1


def test_registration_niftyreg(tmpdir):
    output_directory = os.path.join(str(tmpdir), "output dir")
    brainreg_args = [
        "brainreg",
        str(data_dir),
        output_directory,
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
        str(data_dir),
    ]

    sys.argv = brainreg_args
    brainreg_run()

    # none of this testing is ideal, as results seem to vary between systems

    if platform.system() == "Linux":
        image_list = [
            "boundaries.tiff",
            "deformation_field_0.tiff",
            "deformation_field_1.tiff",
            "deformation_field_2.tiff",
            "downsampled.tiff",
            "downsampled_brain.tiff",
            "downsampled_standard.tiff",
            "downsampled_standard_brain.tiff",
            "registered_atlas.tiff",
            "registered_hemispheres.tiff",
        ]
    else:
        image_list = [
            "boundaries.tiff",
            "deformation_field_0.tiff",
            "deformation_field_1.tiff",
            "deformation_field_2.tiff",
            "downsampled.tiff",
            "downsampled_brain.tiff",
            # "downsampled_standard.tiff",
            # "downsampled_standard_brain.tiff",
            # "registered_atlas.tiff",
            # "registered_hemispheres.tiff",
        ]
    for image in image_list:
        are_images_equal(image, output_directory, str(test_niftyreg_output))

    if platform.system() == "Linux":
        pd.testing.assert_frame_equal(
            pd.read_csv(os.path.join(output_directory, "volumes.csv")),
            pd.read_csv(os.path.join(test_niftyreg_output, "volumes.csv")),
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
