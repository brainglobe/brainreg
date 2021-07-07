import itk

import os
import logging

import numpy as np
import bg_space as bg
import imio

from brainreg.utils import preprocess
from brainreg.backend.elastix.elastix import register


def run_elastix(
    registration_output_folder,
    paths,
    atlas,
    target_brain,
    additional_images_downsample,
    DATA_ORIENTATION,
    ATLAS_ORIENTATION,
    scaling,
    load_parallel,
    sort_input_file,
    n_free_cpus,
    debug=False,
):

    reference = preprocess.filter_image(atlas.reference).astype(np.float32)
    imio.to_tiff(target_brain, paths.downsampled_brain_path)
    target_brain = preprocess.filter_image(target_brain).astype(np.float32)

    logging.info("Registering")
    result_image, result_transform_parameters = register(
        target_brain, reference, log=debug
    )

    logging.info("Starting segmentation")
    moving_image = itk.GetImageViewFromArray(
        atlas.annotation.astype(np.float32)
    )
    result_image = itk.transformix_filter(
        moving_image, result_transform_parameters
    )
    imio.to_tiff(np.asarray(result_image), paths.registered_atlas)

    logging.info("Segmenting hemispheres")
    moving_image = itk.GetImageViewFromArray(
        atlas.hemispheres.astype(np.float32)
    )
    result_image = itk.transformix_filter(
        moving_image, result_transform_parameters
    )
    imio.to_tiff(np.asarray(result_image), paths.registered_hemispheres)

    logging.info("Generating inverse (sample to atlas) transforms")
    result_image, result_transform_parameters = register(
        reference, target_brain, log=debug
    )
    imio.to_tiff(
        np.asarray(result_image), paths.downsampled_brain_standard_space
    )

    if additional_images_downsample:
        logging.info("Saving additional downsampled images")
        for name, filename in additional_images_downsample.items():
            logging.info(f"Processing: {name}")

            downsampled_brain_path = os.path.join(
                registration_output_folder, f"downsampled_{name}.tiff"
            )

            downsampled_brain_standard_path = os.path.join(
                registration_output_folder, f"downsampled_standard_{name}.tiff"
            )

            # do the tiff part at the beginning
            downsampled_brain = imio.load_any(
                filename,
                scaling[1],
                scaling[2],
                scaling[0],
                load_parallel=load_parallel,
                sort_input_file=sort_input_file,
                n_free_cpus=n_free_cpus,
            )

            downsampled_brain = bg.map_stack_to(
                DATA_ORIENTATION, ATLAS_ORIENTATION, downsampled_brain
            ).astype(np.uint16, copy=False)

            imio.to_tiff(downsampled_brain, downsampled_brain_path)

            logging.info("Transforming to standard space")

            moving_image = itk.GetImageViewFromArray(
                downsampled_brain.astype(np.float32)
            )
            result_image = itk.transformix_filter(
                moving_image, result_transform_parameters
            )
            imio.to_tiff(
                np.asarray(result_image), downsampled_brain_standard_path
            )

        del atlas
