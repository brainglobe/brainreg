import os
import logging
import numpy as np

from pathlib import Path
from tqdm import trange

import bgspace as bg
from brainio import brainio

from imlib.general.system import (
    get_num_processes,
    ensure_directory_exists,
    safe_execute_command,
    SafeExecuteCommandError,
)
from imlib.general.exceptions import TransformationError
from imlib.source.niftyreg_binaries import get_binary, get_niftyreg_binaries
from imlib.image.scale import scale_and_convert_to_16_bits

from brainreg.tools import image
from brainreg.paths import Paths, NiftyRegPaths
from brainreg.backend.niftyreg.brain_registration import BrainRegistration
from brainreg.volume import calculate_volumes
from brainreg.boundaries import main as calc_boundaries
from brainreg.backend.niftyreg.registration_params import RegistrationParams
from bg_atlasapi.bg_atlas import AllenBrain25Um


nifty_reg_binaries_folder = get_niftyreg_binaries()


def transform_to_standard_space(
    downsampled_brain,
    downsampled_brain_standard_space,
    template_image,
    inverse_control_point_file_path,
    output_directory,
    PROGRAM_NAME="reg_resample",
):
    program_path = get_binary(nifty_reg_binaries_folder, PROGRAM_NAME)

    reg_cmd = get_registration_cmd(
        program_path,
        downsampled_brain,
        downsampled_brain_standard_space,
        template_image,
        inverse_control_point_file_path,
    )
    niftyreg_directory = Path(output_directory)
    log_file_path = niftyreg_directory / "roi_transform_log.txt"

    error_file_path = niftyreg_directory / "roi_transform_error.txt"

    try:
        safe_execute_command(reg_cmd, log_file_path, error_file_path)
    except SafeExecuteCommandError as err:
        raise TransformationError(
            "Reverse transformation failed; {}".format(err)
        )


def get_transf_matrix_from_res(pix_sizes):
    """ Create transformation matrix in mm
    from a dictionary of pixel sizes in um
    :param pix_sizes:
    :return:
    """
    transformation_matrix = np.eye(4)
    for i, axis in enumerate(("x", "y", "z")):
        transformation_matrix[i, i] = pix_sizes[axis] / 1000
    return transformation_matrix


def filter_plane_for_registration(img_plane):
    """
    Apply a set of filter to the plane (typically to avoid overfitting details
    in the image during registration)
    The filter is composed of a despeckle filter using opening and a pseudo
    flatfield filter

    :param np.array img_plane: A 2D array to filter
    :return: The filtered image
    :rtype: np.array
    """
    img_plane = image.despeckle_by_opening(img_plane)
    img_plane = image.pseudo_flatfield(img_plane)
    return img_plane


def filter_for_registration(brain):
    """
    A static method to filter a 3D image to allow registration
    (avoids overfitting details in the image) (algorithm from Alex Brown).
    The filter is composed of a despeckle filter using opening and a
    pseudo flatfield filter

    :return: The filtered brain
    :rtype: np.array
    """
    brain = brain.astype(np.float64, copy=False)
    # OPTIMISE: could multiprocess but not slow
    for i in trange(brain.shape[-1], desc="filtering", unit="plane"):
        # OPTIMISE: see if in place better
        brain[..., i] = filter_plane_for_registration(brain[..., i])
    brain = scale_and_convert_to_16_bits(brain)
    return brain


def make_hemispheres_stack(shape):
    """ Make stack with hemispheres id. Assumes CCFv3 orientation.
    0: left hemisphere, 1:right hemisphere.
    :param shape: shape of the stack
    :return:
    """
    stack = np.zeros(shape, dtype=np.uint8)
    stack[:, :, (shape[2] // 2) :] = 1

    return stack


def save_nii(stack, atlas_pixel_sizes, dest_path):
    """
    Save self.target_brain to dest_path as a nifty image.
    The scale (zooms of the output nifty image) is copied from the atlas
    brain.

    :param str dest_path: Where to save the image on the filesystem
    """
    transformation_matrix = get_transf_matrix_from_res(atlas_pixel_sizes)
    brainio.to_nii(
        stack,
        dest_path,
        scale=(
            atlas_pixel_sizes["x"] / 1000,
            atlas_pixel_sizes["y"] / 1000,
            atlas_pixel_sizes["z"] / 1000,
        ),
        affine_transform=transformation_matrix,
    )


def get_registration_cmd(
    program_path,
    floating_image_path,
    output_file_name,
    destination_image_filename,
    control_point_file,
):
    # TODO incorporate with main reg class
    cmd = "{} -cpp {} -flo {} -ref {} -res {}".format(
        program_path,
        control_point_file,
        floating_image_path,
        destination_image_filename,
        output_file_name,
    )
    return cmd


def run_niftyreg(
    registration_output_folder,
    paths,
    atlas,
    hemispheres,
    atlas_pixel_sizes,
    target_brain,
    n_processes,
    additional_images_downsample,
    DATA_ORIENTATION,
    ATLAS_ORIENTATION,
    affine_n_steps,
    affine_use_n_steps,
    freeform_n_steps,
    freeform_use_n_steps,
    bending_energy_weight,
    grid_spacing,
    smoothing_sigma_reference,
    smoothing_sigma_floating,
    histogram_n_bins_floating,
    histogram_n_bins_reference,
    target_brain_path,
    x_scaling,
    y_scaling,
    z_scaling,
    load_parallel,
    sort_input_file,
    n_free_cpus,
):
    niftyreg_directory = os.path.join(registration_output_folder, "niftyreg")
    ensure_directory_exists(niftyreg_directory)
    niftyreg_paths = NiftyRegPaths(niftyreg_directory)

    save_nii(hemispheres, atlas_pixel_sizes, niftyreg_paths.hemispheres)

    save_nii(atlas.annotation, atlas_pixel_sizes, niftyreg_paths.annotations)

    reference = filter_for_registration(atlas.reference)
    save_nii(reference, atlas_pixel_sizes, niftyreg_paths.brain_filtered)

    save_nii(target_brain, atlas_pixel_sizes, niftyreg_paths.downsampled_brain)
    brainio.to_tiff(target_brain, paths.downsampled_brain_path)

    target_brain = filter_for_registration(target_brain)
    save_nii(
        target_brain,
        atlas_pixel_sizes,
        niftyreg_paths.tmp__downsampled_filtered,
    )

    logging.info("Registering")

    registration_params = RegistrationParams(
        affine_n_steps=affine_n_steps,
        affine_use_n_steps=affine_use_n_steps,
        freeform_n_steps=freeform_n_steps,
        freeform_use_n_steps=freeform_use_n_steps,
        bending_energy_weight=bending_energy_weight,
        grid_spacing=grid_spacing,
        smoothing_sigma_reference=smoothing_sigma_reference,
        smoothing_sigma_floating=smoothing_sigma_floating,
        histogram_n_bins_floating=histogram_n_bins_floating,
        histogram_n_bins_reference=histogram_n_bins_reference,
    )
    brain_reg = BrainRegistration(
        niftyreg_paths, registration_params, n_processes=n_processes,
    )

    logging.info("Starting affine registration")
    brain_reg.register_affine()

    logging.info("Starting freeform registration")
    brain_reg.register_freeform()

    logging.info("Starting segmentation")
    brain_reg.segment()

    logging.info("Segmenting hemispheres")
    brain_reg.register_hemispheres()

    logging.info("Generating inverse (sample to atlas) transforms")
    brain_reg.generate_inverse_transforms()

    logging.info("Calculating volumes of each brain area")
    calculate_volumes(
        atlas,
        niftyreg_paths.registered_atlas_path,
        niftyreg_paths.hemispheres_atlas_path,
        niftyreg_paths.volume_csv_path,
        # get this from atlas
        left_hemisphere_value=0,
        right_hemisphere_value=1,
    )

    logging.info("Generating boundary image")
    calc_boundaries(
        niftyreg_paths.registered_atlas_path, paths.boundaries_file_path,
    )

    logging.info("Transforming image to standard space")
    transform_to_standard_space(
        niftyreg_paths.downsampled_brain,
        niftyreg_paths.downsampled_brain_standard_space,
        niftyreg_paths.brain_filtered,
        niftyreg_paths.inverse_control_point_file_path,
        niftyreg_directory,
    )

    logging.info("Exporting images as tiff")
    brainio.to_tiff(
        brainio.load_any(niftyreg_paths.annotations), paths.annotations
    )
    brainio.to_tiff(
        brainio.load_any(niftyreg_paths.hemispheres), paths.hemispheres
    )
    brainio.to_tiff(
        brainio.load_any(niftyreg_paths.downsampled_brain_standard_space),
        paths.downsampled_brain_standard_space,
    )

    if additional_images_downsample:
        logging.info("Saving additional downsampled images")
        for name, image in additional_images_downsample.items():
            logging.info(f"Processing: {name}")

            downsampled_brain_path = os.path.join(
                registration_output_folder, f"downsampled_{name}.tiff"
            )
            tmp_downsampled_brain_path = os.path.join(
                niftyreg_directory, f"downsampled_{name}.nii"
            )
            tmp_downsampled_brain_standard_path = os.path.join(
                niftyreg_directory, f"downsampled_standard_{name}.nii"
            )
            downsampled_brain_standard_path = os.path.join(
                registration_output_folder, f"downsampled_standard_{name}.tiff"
            )

            ## do the tiff part at the beginning
            downsampled_brain = brainio.load_any(
                target_brain_path,
                x_scaling,
                y_scaling,
                z_scaling,
                load_parallel=load_parallel,
                sort_input_file=sort_input_file,
                n_free_cpus=n_free_cpus,
            )

            downsampled_brain = bg.map_stack_to(
                DATA_ORIENTATION, ATLAS_ORIENTATION, downsampled_brain
            )

            save_nii(
                downsampled_brain,
                atlas_pixel_sizes,
                tmp_downsampled_brain_path,
            )
            brainio.to_tiff(downsampled_brain, downsampled_brain_path)

            logging.info("Transforming to standard space")
            transform_to_standard_space(
                tmp_downsampled_brain_path,
                tmp_downsampled_brain_standard_path,
                niftyreg_paths.brain_filtered,
                niftyreg_paths.inverse_control_point_file_path,
                niftyreg_directory,
            )
            brainio.to_tiff(
                brainio.load_any(tmp_downsampled_brain_standard_path),
                downsampled_brain_standard_path,
            )

            brainio.to_tiff(
                brainio.load_any(
                    niftyreg_paths.downsampled_brain_standard_space
                ),
                paths.downsampled_brain_standard_space,
            )


def main(
    target_brain_path,
    registration_output_folder,
    x_pixel_um=0.02,
    y_pixel_um=0.02,
    z_pixel_um=0.05,
    affine_n_steps=6,
    affine_use_n_steps=5,
    freeform_n_steps=6,
    freeform_use_n_steps=4,
    bending_energy_weight=0.95,
    grid_spacing=-10,
    smoothing_sigma_reference=-1.0,
    smoothing_sigma_floating=-1.0,
    histogram_n_bins_floating=128,
    histogram_n_bins_reference=128,
    n_free_cpus=2,
    sort_input_file=False,
    additional_images_downsample=None,
    debug=False,
):
    """
        The main function that will perform the library calls and
    register the atlas to the brain given on the CLI

    :param target_brain_path:
    :param registration_output_folder:
    :param filtered_brain_path:
    :param x_pixel_um:
    :param y_pixel_um:
    :param z_pixel_um:
    :param orientation:
    :param flip_x:
    :param flip_y:
    :param flip_z:
    :param n_free_cpus:
    :param sort_input_file:
    :param save_downsampled:
    :param additional_images_downsample: dict of
    {image_name: image_to_be_downsampled}
    :return:
    """
    n_processes = get_num_processes(min_free_cpu_cores=n_free_cpus)
    load_parallel = n_processes > 1

    paths = Paths(registration_output_folder)
    atlas = AllenBrain25Um()

    # TODO: check orientation of atlas voxel sizes
    atlas_pixel_sizes = {
        "x": atlas.metadata["resolution"][0],
        "y": atlas.metadata["resolution"][1],
        "z": atlas.metadata["resolution"][2],
    }

    # TODO: get this from atlas metadata
    ATLAS_ORIENTATION = "asl"

    # TODO: deal with other orientations
    DATA_ORIENTATION = "slp"

    scaling_rounding_decimals = 5

    x_scaling = round(
        x_pixel_um / atlas_pixel_sizes["x"], scaling_rounding_decimals
    )
    y_scaling = round(
        y_pixel_um / atlas_pixel_sizes["y"], scaling_rounding_decimals
    )
    z_scaling = round(
        z_pixel_um / atlas_pixel_sizes["z"], scaling_rounding_decimals
    )

    logging.info("Loading raw image data")
    # TODO: brainio loads in a weird way, eventually it should return "normal"
    # orientation

    target_brain = brainio.load_any(
        target_brain_path,
        x_scaling,
        y_scaling,
        z_scaling,
        load_parallel=load_parallel,
        sort_input_file=sort_input_file,
        n_free_cpus=n_free_cpus,
    )

    target_brain = bg.map_stack_to(
        DATA_ORIENTATION, ATLAS_ORIENTATION, target_brain
    )

    # TODO: incororate this into bg-atlasapi
    hemispheres = make_hemispheres_stack(atlas.reference.shape)

    run_niftyreg(
        registration_output_folder,
        paths,
        atlas,
        hemispheres,
        atlas_pixel_sizes,
        target_brain,
        n_processes,
        additional_images_downsample,
        DATA_ORIENTATION,
        ATLAS_ORIENTATION,
        affine_n_steps,
        affine_use_n_steps,
        freeform_n_steps,
        freeform_use_n_steps,
        bending_energy_weight,
        grid_spacing,
        smoothing_sigma_reference,
        smoothing_sigma_floating,
        histogram_n_bins_floating,
        histogram_n_bins_reference,
        target_brain_path,
        x_scaling,
        y_scaling,
        z_scaling,
        load_parallel,
        sort_input_file,
        n_free_cpus,
    )

    logging.info(
        f"brainreg completed. Results can be found here: "
        f"{registration_output_folder}"
    )
