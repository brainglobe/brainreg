import logging
from brainio import brainio
from skimage.segmentation import find_boundaries
from imlib.image.scale import scale_and_convert_to_16_bits

import numpy as np


def main(registered_atlas, boundaries_out_path):
    atlas_img = brainio.load_nii(registered_atlas)
    atlas_img = np.asanyarray(atlas_img.dataobj)
    boundaries(
        atlas_img, boundaries_out_path,
    )


def boundaries(
    atlas, boundaries_out_path, atlas_labels=False,
):
    """
    Generate the boundary image, which is the border between each segmentation
    region. Useful for overlaying on the raw image to assess the registration
    and segmentation

    :param atlas: The registered atlas
    :param boundaries_out_path: Path to save the boundary image
    :param atlas_labels: If True, keep the numerical values of the atlas for
    the labels
    """
    boundaries_image = find_boundaries(atlas, mode="inner")
    if atlas_labels:
        boundaries_image = boundaries_image * atlas
    boundaries_image = scale_and_convert_to_16_bits(boundaries_image)
    logging.debug("Saving segmentation boundary image")
    brainio.to_tiff(
        boundaries_image, boundaries_out_path,
    )
