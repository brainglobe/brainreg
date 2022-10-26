import os
import traceback as tb
from os.path import isdir


class LoadFileException(Exception):
    """
    Custom exception class for errors found loading image with
    imio.load_any (in main.py).

    If the passed target brain directory contains only a single
    .tiff, alert the user the full filepath including the filename.
    Otherwise, alert the use there was an issue loading the file and
    including the full traceback

    Set the error message to self.message to read during testing.
    """

    def __init__(self, target_brain_path, base_error, error_type=None):

        if error_type == "one_2d_tiff":
            self.message = (
                "Attempted to load directory containing a "
                "single two dimensional .tiff file. Pass "
                "a folder containing 3D tiff file or multiple "
                "2D .tiff files."
            )

        elif error_type is None:

            if self.path_is_folder_with_one_tiff(target_brain_path):
                self.message = (
                    "Attempted to load directory containing single "
                    ".tiff file. For 3D tiff, pass the full path "
                    "including filename."
                )
            else:
                origional_traceback = "".join(
                    tb.format_tb(base_error.__traceback__)
                    + [base_error.__str__()]
                )
                self.message = (
                    f"{origional_traceback}\nFile at {target_brain_path} "
                    f"failed to load. Ensure all image files contain the "
                    f"same number of pixels. Full traceback above."
                )

        super().__init__(self.message)

    def path_is_folder_with_one_tiff(self, target_brain_path):
        """
        Check that the target dir contains only 1 TIFF.
        In this case, the path to the .tiff should be
        passed not the directory.
        """
        if isdir(target_brain_path):
            image_files = self.search_dir_for_image_files(target_brain_path)

            if len(image_files) == 1:
                return True

    @staticmethod
    def search_dir_for_image_files(target_brain_path):
        """
        Search a folder for any images that can be loaded by brainreg

        """
        images_in_dir = [
            file
            for file in os.listdir(target_brain_path)
            if file.lower().endswith((".tif", ".tiff"))
        ]
        return images_in_dir
