"""
image
===============

Image processing functions

"""

from skimage import morphology
from scipy.ndimage import gaussian_filter


def despeckle_by_opening(img_plane, radius=2):  # WARNING: inplace operation
    """
    Despeckle the image plane using a grayscale opening operation

    :param np.array img_plane:
    :param int radius: The radius of the opening kernel
    :return: The despeckled image
    :rtype: np.array
    """
    kernel = morphology.disk(radius)
    morphology.opening(img_plane, out=img_plane, selem=kernel)
    return img_plane


def pseudo_flatfield(img_plane, sigma=5):
    """
    Pseudo flat field filter implementation using a de-trending by a
    heavily gaussian filtered copy of the image.

    :param np.array img_plane: The image to filter
    :param int sigma: The sigma of the gaussian filter applied to the
        image used for de-trending
    :return: The pseudo flat field filtered image
    :rtype: np.array
    """
    img_plane = img_plane.copy()  # OPTIMISE: check if necessary
    filtered_img = gaussian_filter(img_plane, sigma)
    return img_plane / (filtered_img + 1)
