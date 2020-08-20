import logging

import bg_space as bg
import imio

from imlib.general.system import get_num_processes

from brainreg.paths import Paths
from brainreg.backend.niftyreg.run import run_niftyreg

from brainreg.utils.volume import calculate_volumes
from brainreg.utils.boundaries import boundaries


def main(
    atlas,
    data_orientation,
    target_brain_path,
    registration_output_folder,
    niftyreg_args,
    x_pixel_um=0.02,
    y_pixel_um=0.02,
    z_pixel_um=0.05,
    n_free_cpus=2,
    sort_input_file=False,
    additional_images_downsample=None,
    backend="niftyreg",
    debug=False,
):

    n_processes = get_num_processes(min_free_cpu_cores=n_free_cpus)
    load_parallel = n_processes > 1

    paths = Paths(registration_output_folder)

    # TODO: check orientation of atlas voxel sizes
    atlas_pixel_sizes = {
        "x": atlas.metadata["resolution"][0],
        "y": atlas.metadata["resolution"][1],
        "z": atlas.metadata["resolution"][2],
    }

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

    target_brain = imio.load_any(
        target_brain_path,
        x_scaling,
        y_scaling,
        z_scaling,
        load_parallel=load_parallel,
        sort_input_file=sort_input_file,
        n_free_cpus=n_free_cpus,
    )

    target_brain = bg.map_stack_to(
        data_orientation, atlas.metadata["orientation"], target_brain
    )

    if backend == "niftyreg":
        run_niftyreg(
            registration_output_folder,
            paths,
            atlas,
            atlas_pixel_sizes,
            target_brain,
            n_processes,
            additional_images_downsample,
            data_orientation,
            atlas.metadata["orientation"],
            niftyreg_args,
            x_scaling,
            y_scaling,
            z_scaling,
            load_parallel,
            sort_input_file,
            n_free_cpus,
            debug=debug,
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
        paths.registered_atlas, paths.boundaries_file_path,
    )

    logging.info(
        f"brainreg completed. Results can be found here: "
        f"{registration_output_folder}"
    )
