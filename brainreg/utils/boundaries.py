import logging
import imio
from skimage.segmentation import find_boundaries
from imlib.image.scale import scale_and_convert_to_16_bits


def boundaries(
    registered_atlas, boundaries_out_path, atlas_labels=False,
):
    """
    Generate the boundary image, which is the border between each segmentation
    region. Useful for overlaying on the raw image to assess the registration
    and segmentation

    :param registered_atlas: The registered atlas
    :param boundaries_out_path: Path to save the boundary image
    :param atlas_labels: If True, keep the numerical values of the atlas for
    the labels
    """
    atlas_img = imio.load_any(registered_atlas)
    boundaries_image = find_boundaries(atlas_img, mode="inner")
    if atlas_labels:
        boundaries_image = boundaries_image * atlas_img
    boundaries_image = scale_and_convert_to_16_bits(boundaries_image)
    logging.debug("Saving segmentation boundary image")
    imio.to_tiff(
        boundaries_image, boundaries_out_path,
    )
