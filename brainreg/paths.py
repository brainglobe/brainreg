import os


ANNOTATIONS = "annotations.tiff"
HEMISPHERES = "hemispheres.tiff"

INVERSE_CONTROL_POINT = "inverse_control_point_file.nii"


class Paths:
    """
    A single class to hold all file paths that amap may need. Any paths
    prefixed with "tmp__" refer to internal intermediate steps, and will be
    deleted if "--debug" is not used.
    """

    def __init__(self, registration_output_folder):
        self.registration_output_folder = registration_output_folder
        self.make_reg_paths()

    def make_reg_paths(self):
        self.downsampled_brain_path = self.make_reg_path("downsampled.tiff")
        self.downsampled_brain_standard_space = self.make_reg_path(
            "downsampled_standard.tiff"
        )
        self.boundaries_file_path = self.make_reg_path("boundaries.tiff")

        self.hemispheres = self.make_reg_path(HEMISPHERES)
        self.annotations = self.make_reg_path(ANNOTATIONS)

    def make_reg_path(self, basename):
        """
        Compute the absolute path of the destination file to
        self.registration_output_folder.

        :param str basename:
        :return: The path
        :rtype: str
        """
        return os.path.join(self.registration_output_folder, basename)


class NiftyRegPaths:
    """
    A single class to hold all file paths that amap may need. Any paths
    prefixed with "tmp__" refer to internal intermediate steps, and will be
    deleted if "--debug" is not used.
    """

    def __init__(self, registration_output_folder):
        self.registration_output_folder = registration_output_folder
        self.make_reg_paths()

    def make_reg_paths(self):
        self.downsampled_brain = self.make_reg_path("downsampled.nii")
        self.downsampled_brain_standard_space = self.make_reg_path(
            "downsampled_standard.nii"
        )

        self.brain_filtered = self.make_reg_path("brain_filtered.nii")

        self.hemispheres = self.make_reg_path("hemispheres.nii")

        self.annotations = self.make_reg_path("annotations.nii")

        self.tmp__downsampled_filtered = self.make_reg_path(
            "downsampled_filtered.nii"
        )
        self.registered_atlas_path = self.make_reg_path("registered_atlas.nii")
        self.hemispheres_atlas_path = self.make_reg_path(
            "registered_hemispheres.nii"
        )
        self.volume_csv_path = self.make_reg_path("volumes.csv")

        self.tmp__affine_registered_atlas_brain_path = self.make_reg_path(
            "affine_registered_atlas_brain.nii"
        )
        self.tmp__freeform_registered_atlas_brain_path = self.make_reg_path(
            "freeform_registered_atlas_brain.nii"
        )
        self.tmp__inverse_freeform_registered_atlas_brain_path = self.make_reg_path(
            "inverse_freeform_registered_brain.nii"
        )

        self.registered_atlas_img_path = self.make_reg_path(
            "registered_atlas.nii"
        )
        self.registered_hemispheres_img_path = self.make_reg_path(
            "registered_hemispheres.nii"
        )

        self.affine_matrix_path = self.make_reg_path("affine_matrix.txt")
        self.invert_affine_matrix_path = self.make_reg_path(
            "invert_affine_matrix.txt"
        )

        self.control_point_file_path = self.make_reg_path(
            "control_point_file.nii"
        )
        self.inverse_control_point_file_path = self.make_reg_path(
            INVERSE_CONTROL_POINT
        )

        (
            self.tmp__affine_log_file_path,
            self.tmp__affine_error_path,
        ) = self.compute_reg_log_file_paths("affine")
        (
            self.tmp__freeform_log_file_path,
            self.tmp__freeform_error_file_path,
        ) = self.compute_reg_log_file_paths("freeform")
        (
            self.tmp__inverse_freeform_log_file_path,
            self.tmp__inverse_freeform_error_file_path,
        ) = self.compute_reg_log_file_paths("inverse_freeform")
        (
            self.tmp__segmentation_log_file,
            self.tmp__segmentation_error_file,
        ) = self.compute_reg_log_file_paths("segment")
        (
            self.tmp__invert_affine_log_file,
            self.tmp__invert_affine_error_file,
        ) = self.compute_reg_log_file_paths("invert_affine")

    def make_reg_path(self, basename):
        """
        Compute the absolute path of the destination file to
        self.registration_output_folder.

        :param str basename:
        :return: The path
        :rtype: str
        """
        return os.path.join(self.registration_output_folder, basename)

    def compute_reg_log_file_paths(self, basename):
        """
        Compute the path of the log and err file for the step corresponding
        to basename

        :param str basename:
        :return: log_file_path, error_file_path
        """

        log_file_template = os.path.join(
            self.registration_output_folder, "{}.log"
        )
        error_file_template = os.path.join(
            self.registration_output_folder, "{}.err"
        )
        log_file_path = log_file_template.format(basename)
        error_file_path = error_file_template.format(basename)
        return log_file_path, error_file_path
