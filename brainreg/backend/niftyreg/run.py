import os
import logging

import numpy as np

import bg_space as bg
import imio

from imlib.general.system import delete_directory_contents

from brainreg.utils import preprocess
from brainreg.backend.niftyreg.paths import NiftyRegPaths
from brainreg.backend.niftyreg.registration import BrainRegistration
from brainreg.backend.niftyreg.parameters import RegistrationParams
from brainreg.backend.niftyreg.utils import save_nii


def run_niftyreg(
    registration_output_folder,
    paths,
    atlas,
    atlas_pixel_sizes,
    target_brain,
    n_processes,
    additional_images_downsample,
    DATA_ORIENTATION,
    ATLAS_ORIENTATION,
    niftyreg_args,
    x_scaling,
    y_scaling,
    z_scaling,
    load_parallel,
    sort_input_file,
    n_free_cpus,
    debug=False,
):

    niftyreg_directory = os.path.join(registration_output_folder, "niftyreg")

    niftyreg_paths = NiftyRegPaths(niftyreg_directory)

    save_nii(atlas.hemispheres, atlas_pixel_sizes, niftyreg_paths.hemispheres)

    save_nii(atlas.annotation, atlas_pixel_sizes, niftyreg_paths.annotations)

    reference = preprocess.filter_image(atlas.reference)
    save_nii(reference, atlas_pixel_sizes, niftyreg_paths.brain_filtered)

    save_nii(target_brain, atlas_pixel_sizes, niftyreg_paths.downsampled_brain)
    imio.to_tiff(target_brain, paths.downsampled_brain_path)

    target_brain = preprocess.filter_image(target_brain)
    save_nii(
        target_brain, atlas_pixel_sizes, niftyreg_paths.downsampled_filtered,
    )

    logging.info("Registering")

    registration_params = RegistrationParams(
        affine_n_steps=niftyreg_args.affine_n_steps,
        affine_use_n_steps=niftyreg_args.affine_use_n_steps,
        freeform_n_steps=niftyreg_args.freeform_n_steps,
        freeform_use_n_steps=niftyreg_args.freeform_use_n_steps,
        bending_energy_weight=niftyreg_args.bending_energy_weight,
        grid_spacing=niftyreg_args.grid_spacing,
        smoothing_sigma_reference=niftyreg_args.smoothing_sigma_reference,
        smoothing_sigma_floating=niftyreg_args.smoothing_sigma_floating,
        histogram_n_bins_floating=niftyreg_args.histogram_n_bins_floating,
        histogram_n_bins_reference=niftyreg_args.histogram_n_bins_reference,
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

    logging.info("Transforming image to standard space")
    brain_reg.transform_to_standard_space(
        niftyreg_paths.downsampled_brain,
        niftyreg_paths.downsampled_brain_standard_space,
    )

    logging.info("Generating deformation field")
    brain_reg.generate_deformation_field(niftyreg_paths.deformation_field)

    logging.info("Exporting images as tiff")
    imio.to_tiff(
        imio.load_any(niftyreg_paths.registered_atlas_path).astype(
            np.uint32, copy=False
        ),
        paths.registered_atlas,
    )
    imio.to_tiff(
        imio.load_any(niftyreg_paths.registered_hemispheres_img_path).astype(
            np.uint8, copy=False
        ),
        paths.registered_hemispheres,
    )
    imio.to_tiff(
        imio.load_any(niftyreg_paths.downsampled_brain_standard_space).astype(
            np.uint16, copy=False
        ),
        paths.downsampled_brain_standard_space,
    )

    del atlas
    del reference
    del target_brain

    deformation_image = imio.load_any(niftyreg_paths.deformation_field)
    imio.to_tiff(
        deformation_image[..., 0, 0].astype(np.uint32, copy=False),
        paths.deformation_field_0,
    )
    imio.to_tiff(
        deformation_image[..., 0, 1].astype(np.uint32, copy=False),
        paths.deformation_field_1,
    )
    imio.to_tiff(
        deformation_image[..., 0, 2].astype(np.uint32, copy=False),
        paths.deformation_field_2,
    )

    if additional_images_downsample:
        logging.info("Saving additional downsampled images")
        for name, filename in additional_images_downsample.items():
            logging.info(f"Processing: {name}")

            downsampled_brain_path = os.path.join(
                registration_output_folder, f"downsampled_{name}.tiff"
            )
            tmp_downsampled_brain_path = os.path.join(
                niftyreg_paths.niftyreg_directory, f"downsampled_{name}.nii",
            )
            downsampled_brain_standard_path = os.path.join(
                registration_output_folder, f"downsampled_standard_{name}.tiff"
            )
            tmp_downsampled_brain_standard_path = os.path.join(
                niftyreg_paths.niftyreg_directory,
                f"downsampled_standard_{name}.nii",
            )

            # do the tiff part at the beginning
            downsampled_brain = imio.load_any(
                filename,
                x_scaling,
                y_scaling,
                z_scaling,
                load_parallel=load_parallel,
                sort_input_file=sort_input_file,
                n_free_cpus=n_free_cpus,
            )

            downsampled_brain = bg.map_stack_to(
                DATA_ORIENTATION, ATLAS_ORIENTATION, downsampled_brain
            ).astype(np.uint16, copy=False)

            save_nii(
                downsampled_brain,
                atlas_pixel_sizes,
                tmp_downsampled_brain_path,
            )
            imio.to_tiff(downsampled_brain, downsampled_brain_path)

            logging.info("Transforming to standard space")

            brain_reg.transform_to_standard_space(
                tmp_downsampled_brain_path,
                tmp_downsampled_brain_standard_path,
            )

            imio.to_tiff(
                imio.load_any(tmp_downsampled_brain_standard_path).astype(
                    np.uint16, copy=False
                ),
                downsampled_brain_standard_path,
            )

    if not debug:
        logging.info("Deleting intermediate niftyreg files")
        delete_directory_contents(niftyreg_directory)
        os.rmdir(niftyreg_directory)
