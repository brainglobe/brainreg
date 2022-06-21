import numpy as np
from tqdm import trange
from skimage import morphology
from skimage.filters import threshold_triangle
from skimage.measure import label, regionprops
from scipy.ndimage import binary_fill_holes, gaussian_filter
from imlib.image.scale import scale_and_convert_to_16_bits


def filter_image(brain, preprocessing_args=None):
    """
    Filter a 3D image to allow registration
    :return: The filtered brain
    :rtype: np.array
    """
    brain = brain.astype(np.float64, copy=False)
    if preprocessing_args and preprocessing_args.preprocessing == "none":
        pass
    elif preprocessing_args and preprocessing_args.preprocessing == "fmost":
        for i in trange(brain.shape[0], desc="filtering", unit="plane"):  # only coronal plane because of stripes
            brain[i,:,:] = pre_process_fmost(brain[i,:,:])
    else:  # default pre-processing
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


def ideal_notch_filter(fshift, points):
    """
    Remove signature of periodic stripes in the Fourier domain.

    :param fshift: image representation in Fourier domain, with low frequencies shifted to the center
    :param points: coordinates of points corresponding to the striped artifact in Fourier space
    :return: filtered Fourier image representation (fshift)
    :rtype: np.array
    """
    d0 = 5.0  # cutoff frequency
    H, W = fshift.shape
    u, v = np.ogrid[:H, :W]
    for d in range(len(points)):
        u0, v0 = points[d]
        mask1 = (u - u0)**2 + (v - v0)**2 <= d0
        mask2 = (u + u0)**2 + (v + v0)**2 <= d0
        fshift[mask1] = 0
        fshift[mask2] = 0
    return fshift


def remove_stripes(img_plane, stripes_direction="h"):
    """
    Remove vertical or horizontal periodic striped artifacts from image plane.

    Use stripes_direction="h" for horizontal stripes, stripes_direction="v" for vertical stripes.
    Attempting to identify stripes' period using FFT of image plane
    integrated over one dimension (axis 0 for vertical stripes, axis 1 for horizontal stripes)

    :return: The filtered image
    :rtype: np.array
    """
    img_sum = np.sum(img_plane, axis=(1 if stripes_direction == "h" else 0))
    fft_seq = np.abs(np.fft.rfft(img_sum))/img_sum.shape[0]
    first_harmonic = np.argmax(fft_seq[10:]) + 10  # lowest frequencies have extremely high magnitudes
    H, W = img_plane.shape

    # do 2D fft
    img_fft = np.fft.fft2(img_plane.astype(np.float32)) / (W * H)
    # shift fft to get maximum at the center
    img_fft = np.fft.fftshift(img_fft)

    # filter shifted fft
    points = []
    image_center = (H // 2, W // 2)
    if stripes_direction == "h":
        # compute points on vertical axis of symmetry
        for point_ind in range(1, image_center[0] // first_harmonic):
            points.extend([
                [image_center[0] + point_ind * first_harmonic, image_center[1]],
                [image_center[0] - point_ind * first_harmonic, image_center[1]]
            ])
    elif stripes_direction == "v":
        # compute points on horizontal axis of symmetry
        for point_ind in range(1, image_center[1] // first_harmonic):
            points.extend([
                [image_center[0], image_center[1] + point_ind * first_harmonic],
                [image_center[0], image_center[1] - point_ind * first_harmonic]
            ])
    else:
        raise NotImplementedError("Can only automatically remove vertical or horizontal stripes")
    points = np.asarray(points)

    filtered_fft_shift = ideal_notch_filter(img_fft, points)

    # unshift
    img_fft = np.fft.ifftshift(filtered_fft_shift)
    # do inverse fft
    out_ifft = np.fft.ifft2(img_fft)
    img_plane = (np.abs(out_ifft) * W * H)
    return img_plane


def denoise_fft(img_plane):
    """
    Apply circular mask to the image in FFT domain, to keep low frequencies only.
    """
    H, W = img_plane.shape
    img_fft = np.fft.fft2(img_plane)/(W * H)

    img_fft = np.fft.fftshift(img_fft)

    center = [H//2, W//2]
    r = int(min(H, W) / 3)
    x, y = np.ogrid[:H, :W]
    mask_area = (x - center[0])**2 + (y - center[1])**2 >= r**2
    img_fft[mask_area] = 0

    img_fft = np.fft.ifftshift(img_fft)
    out_ifft = np.fft.ifft2(img_fft)

    img_plane = (np.real(out_ifft) * W * H)
    return img_plane


def subtract_background(img_plane):
    """
    Create forground/background mask from image plane.

    Experimental, might not work with some datasets!

    Mask is computed from denoised image with low cutoff frequency
    (blured signigicantly) for better thresholding.
    In the mask, 1 = foreground, 0 = background.
    """
    img_lf = denoise_fft(img_plane)
    try:
        thr = threshold_triangle(img_lf)
    except:  # attempt to get argmax of an empty sequence
        return np.zeros_like(img_plane).astype(np.uint16)

    mask = (img_lf > thr).astype(np.uint8)
    mask = (binary_fill_holes(mask)).astype(np.uint8)
    kernel = morphology.disk(3)
    mask = (morphology.opening(mask, kernel)).astype(np.uint8)
    label_image = label(mask)
    rp = regionprops(label_image)
    rp = sorted(rp, key=lambda x: x.area, reverse=True)
    final_mask = np.zeros_like(mask)
    for i in range(min([5, len(rp)])):  # retain up to 5 largest components
        for c in rp[i].coords:
            final_mask[c[0], c[1]] = 1
    return final_mask


def pre_process_fmost(img_plane):
    foreground_mask = subtract_background(img_plane)
    img_plane = remove_stripes(img_plane)
    img_plane[foreground_mask == 0] = 0
    return img_plane
