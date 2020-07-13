import os


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

        self.registered_atlas = self.make_reg_path("registered_atlas.tiff")
        self.registered_hemispheres = self.make_reg_path(
            "registered_hemispheres.tiff"
        )
        # for each of x,y,z
        self.deformation_field_0 = self.make_reg_path(
            "deformation_field_0.tiff"
        )
        self.deformation_field_1 = self.make_reg_path(
            "deformation_field_1.tiff"
        )
        self.deformation_field_2 = self.make_reg_path(
            "deformation_field_2.tiff"
        )

        self.volume_csv_path = self.make_reg_path("volumes.csv")

    def make_reg_path(self, basename):
        """
        Compute the absolute path of the destination file to
        self.registration_output_folder.

        :param str basename:
        :return: The path
        :rtype: str
        """
        return os.path.join(self.registration_output_folder, basename)
