import os

from brainglobe_utils.general.system import ensure_directory_exists


class AntsPaths:
    def __init__(self, ants_directory):
        self.ants_directory = ants_directory
        ensure_directory_exists(self.ants_directory)
        self.make_ants_paths()

    def make_ants_paths(self):
        """
        Defines the paths to the intermediate files ANTs will generate.
        The `outprefix` will be a path inside the ants_directory.
        """
        self.registration_log = os.path.join(
            self.ants_directory, "ants_registration.log")
        self.output_prefix = os.path.join(self.ants_directory, "ants_reg_")

        # ANTs generates these files based on the prefix
        self.affine_matrix = self.output_prefix + "0GenericAffine.mat"
        self.forward_warp = self.output_prefix + "1Warp.nii.gz"
        self.inverse_warp = self.output_prefix + "1InverseWarp.nii.gz"
        self.warped_atlas_to_sample = self.output_prefix + "Warped.nii.gz"
