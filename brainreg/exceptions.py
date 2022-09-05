import os
import traceback as tb
from os.path import isdir, join


class LoadFileException(Exception):
    """
    Custom exception class for errors found loading image with imio.load_any (in main.py).

    If the passed target brain directory contains only a single .tiff, alert the user the
    full filepath including the filename. Otherwise, alert the use there was an issue loading
    the file and including the full traceback

    TODO: make target_brain_path a class attribute, after determine whether to move
          path_is_folder_with_one_tiff() and search_dir_for_image_files() to utils class.
    """

    def __init__(self, target_brain_path, base_error):

        if self.path_is_folder_with_one_tiff(target_brain_path):
            super().__init__(
                "Attempted to load directory containing single .tiff file. For 3D tiff, pass the full path including filename"
            )
        else:
            origional_traceback = "".join(
                tb.format_tb(base_error.__traceback__) + [base_error.__str__()]
            )
            super().__init__(
                f"{origional_traceback}\nFile at {target_brain_path} failed to load. Full traceback above."
            )

    def path_is_folder_with_one_tiff(self, target_brain_path):
        """
        Check that the target dir contains only 1 TIFF. In this case, the path to the
        .tiff should be passed not the directory.
        """
        if isdir(target_brain_path):
            image_files = self.search_dir_for_image_files(target_brain_path)

            if len(image_files) == 1:
                return True

    @staticmethod
    def search_dir_for_image_files(target_brain_path):
        """
        Search a folder for any images that can be loaded by brainreg

        TODO: - add this to a utils module
              - set a config somewhere that holds all permitted image types to load. This is also needed at niftireg/run
        """
        images_in_dir = [
            file
            for file in os.listdir(target_brain_path)
            if file.lower().endswith((".tif", ".tiff"))
        ]
        return images_in_dir
