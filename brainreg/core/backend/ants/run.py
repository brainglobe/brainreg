import logging
import os

import ants
import brainglobe_space as bg
import numpy as np
from brainglobe_utils.general.system import delete_directory_contents
from brainglobe_utils.IO.image.load import load_any
from brainglobe_utils.IO.image.save import to_tiff

from brainreg.core.backend.ants.paths import AntsPaths
from brainreg.core.backend.ants.registration import AntsRegistration

INTERPOLATOR_MAP = {
    "labels": "genericLabel",
    "image": "linear",
}


def run_ants(
    registration_output_folder,
    paths,  # This is the main brainreg Paths object
    atlas,
    target_brain,  # This is already downsampled and reoriented
    n_processes,
    additional_images_downsample,
    DATA_ORIENTATION,
    ATLAS_ORIENTATION,
    ants_args,
    scaling,
    load_parallel,
    sort_input_file,
    n_free_cpus,
    debug=False,
    save_original_orientation=False,
    # Not directly used by ANTs, but passed for consistency
    brain_geometry="full",
):
    """
    The main function for running the ANTs registration pipeline.
    """
    # --- 1. Setup ---
    ants_directory = os.path.join(registration_output_folder, "ants")
    ants_paths = AntsPaths(ants_directory)

    # --- 2. Prepare images for ANTs ---
    logging.info("Preparing images for ANTs.")
    # Voxel sizes are in mm for ANTs.
    spacing = tuple(res / 1000 for res in atlas.resolution)

    # The 'fixed' image is the one we are registering TO (our sample brain)
    # Ensure it's float32 for ANTs compatibility
    fixed_image_ants = ants.from_numpy(
        target_brain.astype(np.float32), spacing=spacing
    )

    # The 'moving' image is the one that GETS a transform (the atlas)
    moving_image_ants = ants.from_numpy(
        atlas.reference.astype(np.float32), spacing=spacing
    )

    # --- 3. Run Registration ---
    brain_reg = AntsRegistration(ants_paths, ants_args)
    reg_results = brain_reg.run_registration(
        fixed_image=fixed_image_ants,
        moving_image=moving_image_ants,
        verbose=debug,
    )

    # --- 4. Apply transforms and save final outputs ---
    logging.info("Applying final transforms and saving results.")

    # Warp the atlas annotations to the sample space
    registered_atlas_ants = apply_ants_transform(
        fixed_image=fixed_image_ants,
        moving_image_obj=atlas.annotation,
        transformlist=reg_results["fwdtransforms"],
        spacing=spacing,
        interpolator_type="labels",
    )
    to_tiff(registered_atlas_ants.numpy(), paths.registered_atlas)

    # Warp the atlas hemispheres to the sample space
    registered_hemispheres_ants = apply_ants_transform(
        fixed_image=fixed_image_ants,
        moving_image_obj=atlas.hemispheres,
        transformlist=reg_results["fwdtransforms"],
        spacing=spacing,
        interpolator_type="labels",
    )
    to_tiff(registered_hemispheres_ants.numpy(), paths.registered_hemispheres)

    # Warp the original downsampled sample brain to the standard atlas space
    downsampled_brain_standard_space = apply_ants_transform(
        fixed_image=moving_image_ants,  # fixed is now the atlas
        moving_image_obj=target_brain,
        transformlist=reg_results["invtransforms"],
        spacing=spacing,
        interpolator_type="image",
    )
    to_tiff(
        downsampled_brain_standard_space.numpy(),
        paths.downsampled_brain_standard_space,
    )

    # --- 5. Handle "save_original_orientation" feature ---
    if save_original_orientation:
        logging.info("Saving registered atlas in original data orientation.")
        # Remap the warped atlas back to the original data's orientation
        atlas_in_original_orientation = bg.map_stack_to(
            ATLAS_ORIENTATION, DATA_ORIENTATION, registered_atlas_ants.numpy()
        )
        to_tiff(
            atlas_in_original_orientation,
            paths.registered_atlas_original_orientation,
        )

    # --- 6. Handle additional images ---
    if additional_images_downsample:
        logging.info("Processing additional images.")
        for name, filepath in additional_images_downsample.items():
            logging.info(f"--- Processing additional channel: {name} ---")

            # Define standard output paths for this channel
            output_path_sample_space = os.path.join(
                registration_output_folder, f"downsampled_{name}.tiff"
            )
            output_path_standard_space = os.path.join(
                registration_output_folder, f"downsampled_standard_{name}.tiff"
            )

            # Load and downsample the additional channel
            additional_image = load_any(
                filepath,
                scaling[1],
                scaling[2],
                scaling[0],
                load_parallel=load_parallel,
                sort_input_file=sort_input_file,
                n_free_cpus=n_free_cpus,
            )

            # Reorient to atlas space for processing
            additional_image_reoriented = bg.map_stack_to(
                DATA_ORIENTATION, ATLAS_ORIENTATION, additional_image
            )
            # Save the downsampled version in sample space
            to_tiff(additional_image_reoriented, output_path_sample_space)

            # Warp the additional channel to the standard atlas space
            warped_additional_image = apply_ants_transform(
                fixed_image=moving_image_ants,  # fixed is atlas
                moving_image_obj=additional_image_reoriented,
                transformlist=reg_results["invtransforms"],
                spacing=spacing,
                interpolator_type="image",
            )
            to_tiff(
                warped_additional_image.numpy(), output_path_standard_space
            )

    # --- 7. Export Deformation Field (for visualization/analysis) ---
    logging.info("Generating and saving deformation field.")
    # ANTs warp files are 5D (x,y,z,t,vector_component). We need 3D.
    # Load the FORWARD warp (fixed->moving) for the deformation field.
    warp_field_ants = ants.image_read(reg_results["fwdtransforms"][0])
    # The field gives displacement vectors, so it's already float32
    warp_field_numpy = warp_field_ants.numpy()

    # Extract each component and save as a separate TIFF
    to_tiff(warp_field_numpy[..., 0, 0], paths.deformation_field_0)
    to_tiff(warp_field_numpy[..., 0, 1], paths.deformation_field_1)
    to_tiff(warp_field_numpy[..., 0, 2], paths.deformation_field_2)

    # --- 8. Cleanup ---
    if not debug:
        logging.info("Deleting intermediate ANTs files.")
        delete_directory_contents(ants_directory)
        os.rmdir(ants_directory)


def apply_ants_transform(
    fixed_image: ants.ANTsImage,
    moving_image_obj: np.ndarray,
    transformlist: list,
    spacing: tuple,
    interpolator_type: str = "image",
) -> ants.ANTsImage:
    """
    A helper function to apply a computed ANTs transform to a numpy array.

    Parameters
    ----------
    fixed_image : ants.ANTsImage
        The reference image that defines the output space.
    moving_image_obj : np.ndarray
        The numpy array of the image to be warped.
    transformlist : list
        The list of ANTs transform files.
    spacing : tuple
        The voxel spacing in mm for the moving image.
    interpolator_type : str, optional
        The type of interpolation to use ('image' or 'labels'),
        by default "image".

    Returns
    -------
    ants.ANTsImage
        The warped image as an ANTsImage object.
    """
    # Convert numpy array to ANTsImage, ensuring correct type for interpolation
    dtype = np.float32 if interpolator_type == "image" else np.uint32
    moving_image_ants = ants.from_numpy(
        moving_image_obj.astype(dtype, copy=False), spacing=spacing
    )

    # Apply the transform
    warped_image = ants.apply_transforms(
        fixed=fixed_image,
        moving=moving_image_ants,
        transformlist=transformlist,
        interpolator=INTERPOLATOR_MAP[interpolator_type],
    )
    return warped_image
