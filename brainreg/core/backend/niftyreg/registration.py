import logging

from brainglobe_utils.general.system import (
    SafeExecuteCommandError,
    safe_execute_command,
)


class RegistrationError(Exception):
    pass


class SegmentationError(RegistrationError):
    pass


class TransformationError(RegistrationError):
    pass


class BrainRegistration(object):
    """
    A class to register brains using the nifty_reg set of binaries
    """

    def __init__(self, paths, registration_params, n_processes=None):
        self.paths = paths
        self.reg_params = registration_params
        if n_processes is not None:
            self.n_processes = n_processes
            self._prepare_openmp_thread_flag()
        else:
            self.n_processes = None

        self.dataset_img_path = paths.downsampled_filtered
        self.brain_of_atlas_img_path = paths.brain_filtered
        self.atlas_img_path = paths.annotations
        self.hemispheres_img_path = paths.hemispheres

    def _prepare_openmp_thread_flag(self):
        self.openmp_flag = "-omp {}".format(self.n_processes)

    def _prepare_affine_reg_cmd(self):
        cmd = [
            self.reg_params.affine_reg_program_path,
            *self.reg_params.format_affine_params().split(),
            "-flo",
            self.brain_of_atlas_img_path,
            "-ref",
            self.dataset_img_path,
            "-aff",
            self.paths.affine_matrix_path,
            "-res",
            self.paths.affine_registered_atlas_brain_path,
        ]

        if self.n_processes is not None:
            cmd.extend(["-omp", str(self.n_processes)])

        return cmd

    def register_affine(self):
        """
        Performs affine registration of the average brain of the atlas to the
        sample using nifty_reg reg_aladin

        :return:
        :raises RegistrationError: If any error was detected during
            registration.
        """
        try:
            safe_execute_command(
                self._prepare_affine_reg_cmd(),
                self.paths.affine_log_file_path,
                self.paths.affine_error_path,
            )
        except SafeExecuteCommandError as err:
            raise RegistrationError(
                "Affine registration failed; {}".format(err)
            )

    def _prepare_freeform_reg_cmd(self):
        cmd = [
            self.reg_params.freeform_reg_program_path,
            *self.reg_params.format_freeform_params().split(),
            "-aff",
            self.paths.affine_matrix_path,
            "-flo",
            self.brain_of_atlas_img_path,
            "-ref",
            self.dataset_img_path,
            "-cpp",
            self.paths.control_point_file_path,
            "-res",
            self.paths.freeform_registered_atlas_brain_path,
        ]

        if self.n_processes is not None:
            cmd.extend(["-omp", str(self.n_processes)])

        return cmd

    def register_freeform(self):
        """
        Performs freeform (elastic) registration of the average brain of the
        atlas to the sample brain using nifty_reg reg_f3d

        :return:
        :raises RegistrationError: If any error was detected during
            registration.
        """
        try:
            safe_execute_command(
                self._prepare_freeform_reg_cmd(),
                self.paths.freeform_log_file_path,
                self.paths.freeform_error_file_path,
            )
        except SafeExecuteCommandError as err:
            raise RegistrationError(
                "Freeform registration failed; {}".format(err)
            )

    def generate_inverse_transforms(self):
        self.generate_inverse_affine()
        self.register_inverse_freeform()

    def _prepare_invert_affine_cmd(self):
        return [
            self.reg_params.transform_program_path,
            "-invAff",
            self.paths.affine_matrix_path,
            self.paths.invert_affine_matrix_path,
        ]

    def generate_inverse_affine(self):
        """
        Inverts the affine transform to allow for quick registration of the
        sample onto the atlas
        :return:
        :raises RegistrationError: If any error was detected during
            registration.

        """
        logging.debug("Generating inverse affine transform")
        try:
            safe_execute_command(
                self._prepare_invert_affine_cmd(),
                self.paths.invert_affine_log_file,
                self.paths.invert_affine_error_file,
            )
        except SafeExecuteCommandError as err:
            raise RegistrationError(
                "Generation of inverted affine transform failed; "
                "{}".format(err)
            )

    def _prepare_inverse_freeform_reg_cmd(self):
        cmd = [
            self.reg_params.freeform_reg_program_path,
            *self.reg_params.format_freeform_params().split(),
            "-aff",
            self.paths.invert_affine_matrix_path,
            "-flo",
            self.dataset_img_path,
            "-ref",
            self.brain_of_atlas_img_path,
            "-cpp",
            self.paths.inverse_control_point_file_path,
            "-res",
            self.paths.inverse_freeform_registered_atlas_brain_path,
        ]

        if self.n_processes is not None:
            cmd.extend(["-omp", str(self.n_processes)])

        return cmd

    def register_inverse_freeform(self):
        """
        Performs freeform (elastic) registration of the sample to the
        atlas using nifty_reg reg_f3d

        :return:
        :raises RegistrationError: If any error was detected during
            registration.
        """
        logging.debug("Registering sample to atlas")

        try:
            safe_execute_command(
                self._prepare_inverse_freeform_reg_cmd(),
                self.paths.inverse_freeform_log_file_path,
                self.paths.inverse_freeform_error_file_path,
            )
        except SafeExecuteCommandError as err:
            raise RegistrationError(
                "Inverse freeform registration failed; {}".format(err)
            )

    def _prepare_segmentation_cmd(self, floating_image_path, dest_img_path):
        return [
            self.reg_params.segmentation_program_path,
            *self.reg_params.format_segmentation_params().split(),
            "-cpp",
            self.paths.control_point_file_path,
            "-flo",
            floating_image_path,
            "-ref",
            self.dataset_img_path,
            "-res",
            dest_img_path,
        ]

    def _prepare_inverse_registration_cmd(
        self, floating_image_path, dest_img_path
    ):
        return [
            self.reg_params.segmentation_program_path,
            *self.reg_params.format_segmentation_params().split(),
            "-cpp",
            self.paths.inverse_control_point_file_path,
            "-flo",
            floating_image_path,
            "-ref",
            self.brain_of_atlas_img_path,
            "-res",
            dest_img_path,
        ]

    def _prepare_deformation_field_cmd(self, deformation_field_path):
        return [
            self.reg_params.transform_program_path,
            "-def",
            self.paths.control_point_file_path,
            deformation_field_path,
            "-ref",
            self.paths.downsampled_filtered,
        ]

    def segment(self):
        """
        Registers the atlas to the sample (propagates the transformation
        computed for the average brain of the atlas to the atlas itself).


        :return:
        :raises SegmentationError: If any error was detected during the
            propagation.
        """
        try:
            safe_execute_command(
                self._prepare_segmentation_cmd(
                    self.atlas_img_path, self.paths.registered_atlas_img_path
                ),
                self.paths.segmentation_log_file,
                self.paths.segmentation_error_file,
            )
        except SafeExecuteCommandError as err:
            SegmentationError("Segmentation failed; {}".format(err))

    def register_hemispheres(self):
        """
        Registers the hemispheres atlas to the sample (propagates the
        transformation computed for the average brain of the atlas to the
        hemispheres atlas itself).

        :return:
        :raises RegistrationError: If any error was detected during the
            propagation.
        """
        try:
            safe_execute_command(
                self._prepare_segmentation_cmd(
                    self.hemispheres_img_path,
                    self.paths.registered_hemispheres_img_path,
                ),
                self.paths.segmentation_log_file,
                self.paths.segmentation_error_file,
            )
        except SafeExecuteCommandError as err:
            SegmentationError("Segmentation failed; {}".format(err))

    def transform_to_standard_space(self, image_path, destination_path):
        """
        Transform an image in sample space to standard space
        """

        try:
            safe_execute_command(
                self._prepare_inverse_registration_cmd(
                    image_path, destination_path
                ),
                self.paths.inverse_transform_log_file,
                self.paths.inverse_transform_error_file,
            )
        except SafeExecuteCommandError as err:
            raise TransformationError(
                "Reverse transformation failed; {}".format(err)
            )

    def generate_deformation_field(self, deformation_field_path):
        logging.info("Generating deformation field")
        try:
            safe_execute_command(
                self._prepare_deformation_field_cmd(deformation_field_path),
                self.paths.deformation_log_file_path,
                self.paths.deformation_error_file_path,
            )
        except SafeExecuteCommandError as err:
            raise TransformationError(
                "Generation of deformation field failed ; {}".format(err)
            )
