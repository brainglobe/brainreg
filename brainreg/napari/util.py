import logging
from dataclasses import dataclass

import bg_space as bg
import numpy as np
import skimage.transform
from bg_atlasapi import BrainGlobeAtlas
from brainglobe_utils.general.system import get_num_processes
from tqdm import tqdm


def initialise_brainreg(atlas_key, data_orientation_key, voxel_sizes):
    scaling_rounding_decimals = 5
    n_free_cpus = 2
    atlas = BrainGlobeAtlas(atlas_key)
    source_space = bg.AnatomicalSpace(data_orientation_key)

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
    return (
        n_free_cpus,
        n_processes,
        atlas,
        scaling,
        load_parallel,
    )


def downsample_and_save_brain(img_layer, scaling):
    first_frame_shape = skimage.transform.rescale(
        img_layer.data[0], scaling[1:2], anti_aliasing=True
    ).shape
    preallocated_array = np.empty(
        (img_layer.data.shape[0], first_frame_shape[0], first_frame_shape[1])
    )
    print("downsampling data in x, y")
    for i, img in tqdm(enumerate(img_layer.data)):
        down_xy = skimage.transform.rescale(
            img, scaling[1:2], anti_aliasing=True
        )
        preallocated_array[i] = down_xy

    first_ds_frame_shape = skimage.transform.rescale(
        preallocated_array[:, :, 0], [scaling[0], 1], anti_aliasing=True
    ).shape
    downsampled_array = np.empty(
        (first_ds_frame_shape[0], first_frame_shape[0], first_frame_shape[1])
    )
    print("downsampling data in z")
    for i, img in tqdm(enumerate(preallocated_array.T)):
        down_xyz = skimage.transform.rescale(
            img, [1, scaling[0]], anti_aliasing=True
        )
        downsampled_array[:, :, i] = down_xyz.T
    return downsampled_array


@dataclass
class NiftyregArgs:
    """
    Class for niftyreg arguments.
    """

    affine_n_steps: int
    affine_use_n_steps: int
    freeform_n_steps: int
    freeform_use_n_steps: int
    bending_energy_weight: float
    grid_spacing: float
    smoothing_sigma_reference: float
    smoothing_sigma_floating: float
    histogram_n_bins_floating: float
    histogram_n_bins_reference: float
    debug: bool
