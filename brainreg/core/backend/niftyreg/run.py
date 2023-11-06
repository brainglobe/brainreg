import logging
import os
from pathlib import Path

import bg_space as bg
import imio
import numpy as np
from bg_atlasapi import BrainGlobeAtlas
from brainglobe_utils.general.system import delete_directory_contents
from brainglobe_utils.image.scale import scale_and_convert_to_16_bits

from brainreg.core.backend.niftyreg.parameters import RegistrationParams
from brainreg.core.backend.niftyreg.paths import NiftyRegPaths
from brainreg.core.backend.niftyreg.registration import BrainRegistration
from brainreg.core.backend.niftyreg.utils import save_nii
from brainreg.core.utils import preprocess


def crop_atlas(atlas, brain_geometry):
    atlas_cropped = BrainGlobeAtlas(atlas.atlas_name)

    # crop the hemisphere missing from the data
    if brain_geometry == "hemisphere_l":
        ind = atlas_cropped.right_hemisphere_value
    elif brain_geometry == "hemisphere_r":
        ind = atlas_cropped.left_hemisphere_value

    atlas_cropped.reference[atlas_cropped.hemispheres == ind] = 0
    atlas_cropped.annotation[atlas_cropped.hemispheres == ind] = 0

    return atlas_cropped


def run_niftyreg(
    registration_output_folder,
    paths,
    atlas,
    target_brain,
    n_processes,
    additional_images_downsample,
    DATA_ORIENTATION,
    ATLAS_ORIENTATION,
    niftyreg_args,
    preprocessing_args,
    scaling,
    load_parallel,
    sort_input_file,
    n_free_cpus,
    debug=False,
    save_original_orientation=False,
    brain_geometry="full",
):
    niftyreg_directory = os.path.join(registration_output_folder, "niftyreg")

    niftyreg_paths = NiftyRegPaths(niftyreg_directory)

    if brain_geometry != "full":
        atlas_cropped = crop_atlas(atlas, brain_geometry)
        save_nii(
            atlas_cropped.annotation,
            atlas.resolution,
            niftyreg_paths.annotations,
        )
        reference = preprocess.filter_image(atlas_cropped.reference)
    else:
        save_nii(
            atlas.annotation, atlas.resolution, niftyreg_paths.annotations
        )
        reference = preprocess.filter_image(atlas.reference)

    save_nii(atlas.hemispheres, atlas.resolution, niftyreg_paths.hemispheres)
    save_nii(reference, atlas.resolution, niftyreg_paths.brain_filtered)
    save_nii(target_brain, atlas.resolution, niftyreg_paths.downsampled_brain)

    imio.to_tiff(
        scale_and_convert_to_16_bits(target_brain),
        paths.downsampled_brain_path,
    )

    target_brain = preprocess.filter_image(target_brain, preprocessing_args)
    save_nii(
        target_brain, atlas.resolution, niftyreg_paths.downsampled_filtered
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
        niftyreg_paths, registration_params, n_processes=n_processes
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

    if save_original_orientation:
        registered_atlas = imio.load_any(
            niftyreg_paths.registered_atlas_path
        ).astype(np.uint32, copy=False)
        atlas_remapped = bg.map_stack_to(
            ATLAS_ORIENTATION, DATA_ORIENTATION, registered_atlas
        ).astype(np.uint32, copy=False)
        imio.to_tiff(
            atlas_remapped, paths.registered_atlas_original_orientation
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

    del reference
    del target_brain

    deformation_image = imio.load_any(niftyreg_paths.deformation_field)
    imio.to_tiff(
        deformation_image[..., 0, 0].astype(np.float32, copy=False),
        paths.deformation_field_0,
    )
    imio.to_tiff(
        deformation_image[..., 0, 1].astype(np.float32, copy=False),
        paths.deformation_field_1,
    )
    imio.to_tiff(
        deformation_image[..., 0, 2].astype(np.float32, copy=False),
        paths.deformation_field_2,
    )

    if additional_images_downsample:
        logging.info("Saving additional downsampled images")
        for name, filename in additional_images_downsample.items():
            logging.info(f"Processing: {name}")

            name_to_save = (
                Path(name).stem
                if name.lower().endswith((".tiff", ".tif"))
                else name
            )

            downsampled_brain_path = os.path.join(
                registration_output_folder, f"downsampled_{name_to_save}.tiff"
            )
            tmp_downsampled_brain_path = os.path.join(
                niftyreg_paths.niftyreg_directory,
                f"downsampled_{name_to_save}.nii",
            )
            downsampled_brain_standard_path = os.path.join(
                registration_output_folder,
                f"downsampled_standard_{name_to_save}.tiff",
            )
            tmp_downsampled_brain_standard_path = os.path.join(
                niftyreg_paths.niftyreg_directory,
                f"downsampled_standard_{name_to_save}.nii",
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

            save_nii(
                downsampled_brain, atlas.resolution, tmp_downsampled_brain_path
            )

            imio.to_tiff(downsampled_brain, downsampled_brain_path)

            logging.info("Transforming to standard space")

            brain_reg.transform_to_standard_space(
                tmp_downsampled_brain_path, tmp_downsampled_brain_standard_path
            )

            imio.to_tiff(
                imio.load_any(tmp_downsampled_brain_standard_path).astype(
                    np.uint16, copy=False
                ),
                downsampled_brain_standard_path,
            )
        del atlas

    if not debug:
        logging.info("Deleting intermediate niftyreg files")
        delete_directory_contents(niftyreg_directory)
        os.rmdir(niftyreg_directory)
