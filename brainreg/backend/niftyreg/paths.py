import os
from imlib.general.system import ensure_directory_exists


class NiftyRegPaths:
    def __init__(self, niftyreg_directory):
        self.niftyreg_directory = niftyreg_directory
        ensure_directory_exists(self.niftyreg_directory)
        self.make_reg_paths()

    def make_reg_paths(self):
        self.downsampled_brain = self.make_reg_path("downsampled.nii")
        self.downsampled_brain_standard_space = self.make_reg_path(
            "downsampled_standard.nii"
        )

        self.brain_filtered = self.make_reg_path("brain_filtered.nii")

        self.hemispheres = self.make_reg_path("hemispheres.nii")

        self.annotations = self.make_reg_path("annotations.nii")

        self.downsampled_filtered = self.make_reg_path(
            "downsampled_filtered.nii"
        )
        self.registered_atlas_path = self.make_reg_path("registered_atlas.nii")
        self.hemispheres_atlas_path = self.make_reg_path(
            "registered_hemispheres.nii"
        )

        self.affine_registered_atlas_brain_path = self.make_reg_path(
            "affine_registered_atlas_brain.nii"
        )
        self.freeform_registered_atlas_brain_path = self.make_reg_path(
            "freeform_registered_atlas_brain.nii"
        )
        self.inverse_freeform_registered_atlas_brain_path = self.make_reg_path(
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
            "inverse_control_point_file.nii"
        )

        self.deformation_field = self.make_reg_path("deformation_field.nii")
        (
            self.deformation_log_file_path,
            self.deformation_error_file_path,
        ) = self.compute_reg_log_file_paths("deformation")

        (
            self.affine_log_file_path,
            self.affine_error_path,
        ) = self.compute_reg_log_file_paths("affine")
        (
            self.freeform_log_file_path,
            self.freeform_error_file_path,
        ) = self.compute_reg_log_file_paths("freeform")
        (
            self.inverse_freeform_log_file_path,
            self.inverse_freeform_error_file_path,
        ) = self.compute_reg_log_file_paths("inverse_freeform")
        (
            self.segmentation_log_file,
            self.segmentation_error_file,
        ) = self.compute_reg_log_file_paths("segment")
        (
            self.inverse_transform_log_file,
            self.inverse_transform_error_file,
        ) = self.compute_reg_log_file_paths("inverse_transform")
        (
            self.invert_affine_log_file,
            self.invert_affine_error_file,
        ) = self.compute_reg_log_file_paths("invert_affine")

    def make_reg_path(self, basename):
        """
        Compute the absolute path of the destination file to
        self.registration_output_folder.

        :param str basename:
        :return: The path
        :rtype: str
        """
        return os.path.join(self.niftyreg_directory, basename)

    def compute_reg_log_file_paths(self, basename):
        """
        Compute the path of the log and err file for the step corresponding
        to basename

        :param str basename:
        :return: log_file_path, error_file_path
        """

        log_file_template = os.path.join(self.niftyreg_directory, "{}.log")
        error_file_template = os.path.join(self.niftyreg_directory, "{}.err")
        log_file_path = log_file_template.format(basename)
        error_file_path = error_file_template.format(basename)
        return log_file_path, error_file_path
