import logging

from pathlib import Path


class Run:
    """
    Determines what parts of brainreg to run, based on what files already exist
    """

    def __init__(
        self,
        paths,
        atlas,
        boundaries=True,
        additional_images=False,
        debug=False,
    ):
        self._paths = paths
        self._atlas = atlas
        self._boundaries = boundaries
        self._additional_images = additional_images
        self._debug = debug

    # TODO: make this more specific
    @property
    def preprocess(self):
        if (
            self._brain_exists
            and self._atlas_exists
            and self._hemispheres_exists
            and self._downsampled_filtered_exists
        ):
            logging.info(
                "Downsampled data and reoriented atlas exists, skipping."
            )
            return False
        else:
            return True

    @property
    def register(self):
        if (
            self._registered_atlas_exists
            and self._registered_hemispheres_exists
            and self._inverse_control_point_exists
        ):
            logging.info("Registration allready completed, skipping")
            return False
        else:
            return True

    @property
    def affine(self):
        if self.register and not (
            self._affine_reg_brain_exists or self._control_point_exists
        ):
            return True
        else:
            logging.info("Affine registration allready completed, skipping")
            return False

    @property
    def freeform(self):
        if self.register and not self._control_point_exists:
            return True
        else:
            logging.info("Freeform registration already completed, skipping.")
            return False

    @property
    def segment(self):
        if self._registered_atlas_exists:
            logging.info("Registered atlas exists, skipping segmentation")
            return False
        else:
            return True

    @property
    def hemispheres(self):
        if self._registered_hemispheres_exists:
            logging.info("Registered hemispheres exist, skipping segmentation")
            return False
        else:
            return True

    @property
    def inverse_transform(self):
        if self._inverse_control_point_exists:
            logging.info(
                "Inverse transform exists, skipping inverse registration"
            )
            return False
        else:
            return True

    @property
    def volumes(self):
        if self._volumes_exist:
            logging.info(
                "Volumes csv exists, skipping region volume calculation"
            )
            return False
        else:
            return True

    @property
    def boundaries(self):
        if self._boundaries:
            if self._boundaries_exist:
                logging.info(
                    "Boundary image exists, skipping boundary image generation"
                )
                return False
            else:
                return True
        else:
            logging.info("Boundary image deselected, not generating")
            return False

    @property
    def delete_temp(self):
        return not self._debug

    @property
    def _atlas_exists(self):
        return self._exists(self._atlas.get_dest_path("atlas_name"))

    @property
    def _brain_exists(self):
        return self._exists(self._atlas.get_dest_path("brain_name"))

    @property
    def _hemispheres_exists(self):
        return self._exists(self._atlas.get_dest_path("hemispheres_name"))

    @property
    def _downsampled_exists(self):
        return self._exists(self._paths.downsampled_brain_path)

    @property
    def _downsampled_filtered_exists(self):
        return self._exists(self._paths.tmp__downsampled_filtered)

    @property
    def _affine_exists(self):
        return self._exists(self._paths.affine_matrix_path)

    @property
    def _affine_reg_brain_exists(self):
        return self._exists(
            self._paths.tmp__affine_registered_atlas_brain_path
        )

    @property
    def _control_point_exists(self):
        return self._exists(self._paths.control_point_file_path)

    @property
    def _inverse_control_point_exists(self):
        return self._exists(self._paths.inverse_control_point_file_path)

    @property
    def _registered_atlas_exists(self):
        return self._exists(self._paths.registered_atlas_path)

    @property
    def _registered_hemispheres_exists(self):
        return self._exists(self._paths.registered_hemispheres_img_path)

    @property
    def _volumes_exist(self):
        return self._exists(self._paths.volume_csv_path)

    @property
    def _boundaries_exist(self):
        return self._exists(self._paths.boundaries_file_path)

    @staticmethod
    def _exists(path):
        if isinstance(path, Path):
            return path.exists()
        else:
            return Path(path).exists()
