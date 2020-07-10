import numpy as np
from tqdm import trange
from skimage import morphology
from scipy.ndimage import gaussian_filter
from imlib.image.scale import scale_and_convert_to_16_bits


def filter_image(brain):
    """
    Filter a 3D image to allow registration
    :return: The filtered brain
    :rtype: np.array
    """
    brain = brain.astype(np.float64, copy=False)
    for i in trange(brain.shape[-1], desc="filtering", unit="plane"):
        brain[..., i] = filter_plane(brain[..., i])
    brain = scale_and_convert_to_16_bits(brain)
    return brain


def filter_plane(img_plane):
    """
    Apply a set of filter to the plane (typically to avoid overfitting details
    in the image during registration)
    The filter is composed of a despeckle filter using opening and a pseudo
    flatfield filter

    :param np.array img_plane: A 2D array to filter
    :return: The filtered image
    :rtype: np.array
    """
    img_plane = despeckle_by_opening(img_plane)
    img_plane = pseudo_flatfield(img_plane)
    return img_plane


def despeckle_by_opening(img_plane, radius=2):
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
    filtered_img = gaussian_filter(img_plane, sigma)
    return img_plane / (filtered_img + 1)
