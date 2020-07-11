from imlib.source.niftyreg_binaries import get_niftyreg_binaries, get_binary


class RegistrationParams:
    """
    A class to store and access the variables required for the registration
    including the paths of the different binaries and atlases.
    Options are typically stored as a tuple of (option_string, option_value)
    """

    def __init__(
        self,
        affine_n_steps=6,
        affine_use_n_steps=5,
        freeform_n_steps=6,
        freeform_use_n_steps=4,
        bending_energy_weight=0.95,
        grid_spacing=-10,
        smoothing_sigma_reference=-1.0,
        smoothing_sigma_floating=-1.0,
        histogram_n_bins_floating=128,
        histogram_n_bins_reference=128,
    ):
        self.transform_program_path = self.__get_binary("transform")
        self.affine_reg_program_path = self.__get_binary("affine")
        self.freeform_reg_program_path = self.__get_binary("freeform")
        self.segmentation_program_path = self.__get_binary("segmentation")

        # affine (reg_aladin)
        self.affine_reg_pyramid_steps = ("-ln", affine_n_steps)
        self.affine_reg_used_pyramid_steps = ("-lp", affine_use_n_steps)

        # freeform (ref_f3d)
        self.freeform_reg_pyramid_steps = ("-ln", freeform_n_steps)
        self.freeform_reg_used_pyramid_steps = ("-lp", freeform_use_n_steps)

        self.freeform_reg_grid_spacing = ("-sx", grid_spacing)

        self.bending_energy_penalty_weight = ("-be", bending_energy_weight)

        self.reference_image_smoothing_sigma = (
            "-smooR",
            smoothing_sigma_reference,
        )
        self.floating_image_smoothing_sigma = (
            "-smooF",
            smoothing_sigma_floating,
        )

        self.reference_image_histo_n_bins = (
            "--rbn",
            histogram_n_bins_reference,
        )
        self.floating_image_histo_n_bins = ("--fbn", histogram_n_bins_floating)

        # segmentation (reg_resample)
        self.segmentation_interpolation_order = ("-inter", 0)

    def get_affine_reg_params(self):
        """
        Get the parameters (options) required for the affine registration step

        :return: The affine registration options.
        :rtype: list
        """
        affine_params = [
            self.affine_reg_pyramid_steps,
            self.affine_reg_used_pyramid_steps,
        ]
        return affine_params

    def get_freeform_reg_params(self):
        """
        Get the parameters (options) required for the freeform (elastic)
        registration step

        :return: The freeform registration options.
        :rtype: list
        """
        freeform_params = [
            self.freeform_reg_pyramid_steps,
            self.freeform_reg_used_pyramid_steps,
            self.freeform_reg_grid_spacing,
            self.bending_energy_penalty_weight,
            self.reference_image_smoothing_sigma,
            self.floating_image_smoothing_sigma,
            self.reference_image_histo_n_bins,
            self.floating_image_histo_n_bins,
        ]
        return freeform_params

    def get_segmentation_params(self):
        """
        Get the parameters (options) required for the segmentation step
        (propagation of transformation)

        :return: The affine registration options.
        :rtype: list
        """
        return [self.segmentation_interpolation_order]

    def format_param_pairs(self, params_pairs):
        """
        Format the list of params pairs into a string

        :param list params_pairs: A list of tuples of the form
            (option_string, option_value) (e.g. (-sx, 10))
        :return: The options as a formatted string
        :rtype: str
        """
        out = ""
        for param in params_pairs:
            out += "{} {} ".format(*param)
        return out

    def format_affine_params(self):
        """
        Generate the string of formatted affine registration options

        :return: The formatted string
        :rtype: str
        """
        return self.format_param_pairs(self.get_affine_reg_params())

    def format_freeform_params(self):
        """
        Generate the string of formatted freeform registration options

        :return: The formatted string
        :rtype: str
        """
        return self.format_param_pairs(self.get_freeform_reg_params())

    def format_segmentation_params(self):
        """
        Generate the string of formatted segmentation options

        :return: The formatted string
        :rtype: str
        """
        return self.format_param_pairs(self.get_segmentation_params())

    def __get_binary(self, program_type):
        """
        Get the path to the registration (from nifty_reg) program
        based on the type

        :param str program_type:
        :return: The program path
        :rtype: str
        """

        program_names = {
            "affine": "reg_aladin",
            "freeform": "reg_f3d",
            "segmentation": "reg_resample",
            "transform": "reg_transform",
        }
        program_name = program_names[program_type]
        nifty_reg_binaries_folder = get_niftyreg_binaries()

        program_path = get_binary(nifty_reg_binaries_folder, program_name)

        return program_path
