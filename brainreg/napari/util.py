import logging
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass

import brainglobe_space as bg
import numpy as np
import skimage.transform
from brainglobe_atlasapi import BrainGlobeAtlas
from brainglobe_utils.general.system import get_num_processes
from tqdm import tqdm


def initialise_brainreg(
    atlas_key, data_orientation_key, voxel_sizes, n_free_cpus=2
):
    scaling_rounding_decimals = 5
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


def downsample_and_save_brain(
    img_layer,
    scaling,
    n_processes=1,
    anti_aliasing=True,
    preserve_range=True,
    mode="constant",
):
    first_frame_shape = skimage.transform.rescale(
        np.asarray(img_layer.data[0]),
        scaling[1:2],
        anti_aliasing=anti_aliasing,
        preserve_range=preserve_range,
        mode=mode,
    ).shape
    preallocated_array = np.empty(
        (img_layer.data.shape[0], first_frame_shape[0], first_frame_shape[1])
    )
    print("Downsampling data in x, y")

    def downsample_plane(i):
        # np.asarray: a lazy (dask) layer is otherwise recomputed several times
        # inside rescale, i.e. re-read from disk once per internal step.
        preallocated_array[i] = skimage.transform.rescale(
            np.asarray(img_layer.data[i]),
            scaling[1:2],
            anti_aliasing=anti_aliasing,
            preserve_range=preserve_range,
            mode=mode,
        )

    n_planes = img_layer.data.shape[0]
    with ThreadPoolExecutor(max_workers=n_processes) as executor:
        list(
            tqdm(
                executor.map(downsample_plane, range(n_planes)),
                total=n_planes,
                unit="plane",
            )
        )

    first_ds_frame_shape = skimage.transform.rescale(
        preallocated_array[:, :, 0],
        [scaling[0], 1],
        anti_aliasing=anti_aliasing,
        preserve_range=preserve_range,
        mode=mode,
    ).shape
    downsampled_array = np.empty(
        (first_ds_frame_shape[0], first_frame_shape[0], first_frame_shape[1])
    )
    print("Downsampling data in z")
    for i, img in tqdm(enumerate(preallocated_array.T)):
        down_xyz = skimage.transform.rescale(
            img,
            [1, scaling[0]],
            anti_aliasing=anti_aliasing,
            preserve_range=preserve_range,
            mode=mode,
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
