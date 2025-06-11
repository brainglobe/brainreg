import logging

import ants


class AntsRegistration:
    """
    A class to peform registration using the ANTsPy library.
    """

    def __init__(self, ants_paths, ants_reg_params):
        """
        Parameters
        ----------
        ants_paths : AntsPaths
            An object that holds the paths to all the intermediate files
            that ANTs will generate.
        ants_reg_params : argparse.Namespace
            The ANTs-specific arguments parsed from the command line.
        """
        self.paths = ants_paths
        self.params = ants_reg_params

    def run_registration(self, fixed_image, moving_image, verbose=False):
        """
        Performs registration using ants.registration().

        The transform type and other parameters are taken from the
        initialised class attributes.

        Parameters
        ----------
        fixed_image : ants.ANTsImage
            The image to which the moving_image is registered.
            In our case, this is the sample brain.
        moving_image : ants.ANTsImage
            The image that is registered to the fixed_image.
            In our case, this is the atlas reference brain.
        verbose : bool
            Whether to print the ANTs command to the console.
        """
        logging.info("--- Running ANTs registration ---")
        logging.info(f"Transform type: {self.params.ants_transform_type}")

        # The core ANTs call. We pass the parameters directly.
        # The 'outprefix' ensures all files are saved in our temp directory.
        registration_results = ants.registration(
            fixed=fixed_image,
            moving=moving_image,
            type_of_transform=self.params.ants_transform_type,
            outprefix=self.paths.output_prefix,
            verbose=verbose,
        )

        logging.info("--- ANTs registration finished ---")

        # The registration_results dictionary contains the paths to the
        # generated transforms.
        return registration_results
