import numpy as np
import imio


def save_nii(stack, atlas_pixel_sizes, dest_path):
    """
    Save self.target_brain to dest_path as a nifti image.
    The scale (zooms of the output nifti image) is copied from the atlas
    brain.

    :param str dest_path: Where to save the image on the filesystem
    """
    transformation_matrix = get_transf_matrix_from_res(atlas_pixel_sizes)
    imio.to_nii(
        stack,
        dest_path,
        scale=(
            atlas_pixel_sizes["x"] / 1000,
            atlas_pixel_sizes["y"] / 1000,
            atlas_pixel_sizes["z"] / 1000,
        ),
        affine_transform=transformation_matrix,
    )


def get_transf_matrix_from_res(pix_sizes):
    """ Create transformation matrix in mm
    from a dictionary of pixel sizes in um
    :param pix_sizes:
    :return:
    """
    transformation_matrix = np.eye(4)
    for i, axis in enumerate(("x", "y", "z")):
        transformation_matrix[i, i] = pix_sizes[axis] / 1000
    return transformation_matrix
