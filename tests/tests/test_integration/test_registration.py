import os
import platform
import sys
from pathlib import Path

import pytest

from brainreg.cli import main as brainreg_run

from .utils import check_images_same, check_volumes_equal

if platform.system() == "Darwin":
    if platform.machine() == "x86_64":
        test_dir = "Darwin_intel"
    else:
        test_dir = "Darwin_arm"
else:
    test_dir = platform.system()

test_data_dir = Path(os.getcwd()) / "tests" / "data"

whole_brain_data_dir = test_data_dir / "input" / "brain"
whole_brain_expected_output_dir = (
    test_data_dir / "registration_output" / test_dir
)

hemisphere_data_dir = test_data_dir / "input" / "hemisphere_l"
hemisphere_expected_output_dir = (
    test_data_dir / "registration_output" / "hemisphere_l" / test_dir
)

whole_brain_voxel_sizes = ("50", "40", "40")
hemisphere_voxel_sizes = ("100", "100", "100")


@pytest.fixture(scope="session")
def whole_brain_output_path(tmp_path_factory):
    test_output_dir = tmp_path_factory.mktemp("output_dir")
    brainreg_args = [
        "brainreg",
        str(whole_brain_data_dir),
        str(test_output_dir),
        "-v",
        whole_brain_voxel_sizes[0],
        whole_brain_voxel_sizes[1],
        whole_brain_voxel_sizes[2],
        "--orientation",
        "psl",
        "--n-free-cpus",
        "0",
        "--atlas",
        "allen_mouse_100um",
        "-a",
        str(whole_brain_data_dir),
    ]

    sys.argv = brainreg_args
    brainreg_run()
    return test_output_dir


@pytest.fixture(scope="session")
def hemisphere_output_path(tmp_path_factory):
    test_output_dir = tmp_path_factory.mktemp("hemisphere_output_dir")
    brainreg_args = [
        "brainreg",
        str(hemisphere_data_dir),
        str(test_output_dir),
        "-v",
        hemisphere_voxel_sizes[0],
        hemisphere_voxel_sizes[1],
        hemisphere_voxel_sizes[2],
        "--orientation",
        "asr",
        "--n-free-cpus",
        "0",
        "--atlas",
        "allen_mouse_100um",
        "--brain_geometry",
        "hemisphere_l",
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
        "downsampled_brain.tiff",
        "downsampled_standard.tiff",
        "downsampled_standard_brain.tiff",
        "registered_atlas.tiff",
        "registered_hemispheres.tiff",
    ],
)
def test_whole_brain(whole_brain_output_path, image):
    check_images_same(
        image, whole_brain_output_path, whole_brain_expected_output_dir
    )
    check_volumes_equal(
        whole_brain_output_path, whole_brain_expected_output_dir
    )


@pytest.mark.parametrize(
    "image",
    [
        "boundaries.tiff",
        "deformation_field_0.tiff",
        "deformation_field_1.tiff",
        "deformation_field_2.tiff",
        "downsampled.tiff",
        "downsampled_standard.tiff",
        "registered_atlas.tiff",
        "registered_hemispheres.tiff",
    ],
)
def test_hemisphere(hemisphere_output_path, image):
    check_images_same(
        image, hemisphere_output_path, hemisphere_expected_output_dir
    )
    check_volumes_equal(hemisphere_output_path, hemisphere_expected_output_dir)
