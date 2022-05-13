import logging

import bg_space as bg
import imio

from imlib.general.system import get_num_processes

from brainreg.backend.niftyreg.run import run_niftyreg

from brainreg.utils.volume import calculate_volumes
from brainreg.utils.boundaries import boundaries

from bg_atlasapi import BrainGlobeAtlas


def main(
    atlas,
    data_orientation,
    target_brain_path,
    paths,
    voxel_sizes,
    niftyreg_args,
    n_free_cpus=2,
    sort_input_file=False,
    additional_images_downsample=None,
    backend="niftyreg",
    scaling_rounding_decimals=5,
    debug=False,
    save_original_orientation=False,
):
    atlas = BrainGlobeAtlas(atlas)
    source_space = bg.AnatomicalSpace(data_orientation)

    scaling = []
    for idx, axis in enumerate(atlas.space.axes_order):
        scaling.append(
            round(
                float(voxel_sizes[idx])
                / atlas.resolution[
                    atlas.space.axes_order.index(source_space.axes_order[idx])
                ],
                scaling_rounding_decimals,
            )
        )

    n_processes = get_num_processes(min_free_cpu_cores=n_free_cpus)
    load_parallel = n_processes > 1

    logging.info("Loading raw image data")
    target_brain = imio.load_any(
        target_brain_path,
        scaling[1],
        scaling[2],
        scaling[0],
        load_parallel=load_parallel,
        sort_input_file=sort_input_file,
        n_free_cpus=n_free_cpus,
    )

    target_brain = bg.map_stack_to(
        data_orientation, atlas.metadata["orientation"], target_brain
    )

    if backend == "niftyreg":
        run_niftyreg(
            paths.registration_output_folder,
            paths,
            atlas,
            target_brain,
            n_processes,
            additional_images_downsample,
            data_orientation,
            atlas.metadata["orientation"],
            niftyreg_args,
            scaling,
            load_parallel,
            sort_input_file,
            n_free_cpus,
            debug=debug,
            save_original_orientation=save_original_orientation,
        )

    logging.info("Calculating volumes of each brain area")
    calculate_volumes(
        atlas,
        paths.registered_atlas,
        paths.registered_hemispheres,
        paths.volume_csv_path,
        # for all brainglobe atlases
        left_hemisphere_value=1,
        right_hemisphere_value=2,
    )

    logging.info("Generating boundary image")
    boundaries(
        paths.registered_atlas,
        paths.boundaries_file_path,
    )

    logging.info(
        f"brainreg completed. Results can be found here: "
        f"{paths.registration_output_folder}"
    )
