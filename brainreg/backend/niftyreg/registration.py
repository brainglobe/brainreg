import logging


from imlib.general.system import (
    safe_execute_command,
    SafeExecuteCommandError,
)

from imlib.general.exceptions import (
    RegistrationError,
    SegmentationError,
    TransformationError,
)


class BrainRegistration(object):
    """
    A class to register brains using the nifty_reg set of binaries
    """

    def __init__(
        self, paths, registration_params, n_processes=None,
    ):
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
        cmd = "{} {} -flo {} -ref {} -aff {} -res {}".format(
            self.reg_params.affine_reg_program_path,
            self.reg_params.format_affine_params().strip(),
            self.brain_of_atlas_img_path,
            self.dataset_img_path,
            self.paths.affine_matrix_path,
            self.paths.affine_registered_atlas_brain_path,
        )

        if self.n_processes is not None:
            cmd += " " + self.openmp_flag
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
        cmd = "{} {} -aff {} -flo {} -ref {} -cpp {} -res {}".format(
            self.reg_params.freeform_reg_program_path,
            self.reg_params.format_freeform_params().strip(),
            self.paths.affine_matrix_path,
            self.brain_of_atlas_img_path,
            self.dataset_img_path,
            self.paths.control_point_file_path,
            self.paths.freeform_registered_atlas_brain_path,
        )

        if self.n_processes is not None:
            cmd += " " + self.openmp_flag
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
        cmd = "{} -invAff {} {}".format(
            self.reg_params.transform_program_path,
            self.paths.affine_matrix_path,
            self.paths.invert_affine_matrix_path,
        )
        return cmd

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
        cmd = "{} {} -aff {} -flo {} -ref {} -cpp {} -res {}".format(
            self.reg_params.freeform_reg_program_path,
            self.reg_params.format_freeform_params().strip(),
            self.paths.invert_affine_matrix_path,
            self.dataset_img_path,
            self.brain_of_atlas_img_path,
            self.paths.inverse_control_point_file_path,
            self.paths.inverse_freeform_registered_atlas_brain_path,
        )

        if self.n_processes is not None:
            cmd += " " + self.openmp_flag
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
        cmd = "{} {} -cpp {} -flo {} -ref {} -res {}".format(
            self.reg_params.segmentation_program_path,
            self.reg_params.format_segmentation_params().strip(),
            self.paths.control_point_file_path,
            floating_image_path,
            self.dataset_img_path,
            dest_img_path,
        )
        return cmd

    def _prepare_inverse_registration_cmd(
        self, floating_image_path, dest_img_path
    ):
        cmd = "{} {} -cpp {} -flo {} -ref {} -res {}".format(
            self.reg_params.segmentation_program_path,
            self.reg_params.format_segmentation_params().strip(),
            self.paths.inverse_control_point_file_path,
            floating_image_path,
            self.brain_of_atlas_img_path,
            dest_img_path,
        )
        return cmd

    def _prepare_deformation_field_cmd(self, deformation_field_path):
        cmd = "{} -def {} {} -ref {}".format(
            self.reg_params.transform_program_path,
            self.paths.control_point_file_path,
            deformation_field_path,
            self.paths.downsampled_filtered,
        )
        return cmd

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
                    image_path, destination_path,
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
