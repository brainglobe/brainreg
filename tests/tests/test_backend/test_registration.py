from unittest.mock import Mock, patch

import pytest
from brainglobe_utils.general.system import SafeExecuteCommandError

from brainreg.core.backend.niftyreg.registration import (
    BrainRegistration,
    SegmentationError,
)


def _make_registration():
    """
    Create a minimal BrainRegistration instance with mocked paths
    and registration parameters.
    """
    paths = Mock()
    paths.segmentation_log_file = "seg.log"
    paths.segmentation_error_file = "seg.err"
    paths.registered_atlas_img_path = "registered_atlas.nii"
    paths.control_point_file_path = "cpp.nii"
    paths.downsampled_filtered = "ref.nii"
    paths.annotations = "atlas.nii"

    reg_params = Mock()
    reg_params.segmentation_program_path = "reg_resample"
    reg_params.format_segmentation_params.return_value = ""

    return BrainRegistration(
        paths=paths,
        registration_params=reg_params,
        n_processes=None,
    )


def test_segment_raises_segmentation_error():
    """
    Ensure SegmentationError is raised when the command fails.
    """
    reg = _make_registration()

    with patch(
        "brainreg.core.backend.niftyreg.registration.safe_execute_command",
        side_effect=SafeExecuteCommandError("command failed"),
    ):
        with pytest.raises(SegmentationError):
            reg.segment()


def test_register_hemispheres_raises_segmentation_error():
    """
    Ensure SegmentationError is raised when hemisphere registration fails.
    """
    reg = _make_registration()

    # extra path used by register_hemispheres
    reg.paths.hemispheres = "hemi.nii"
    reg.paths.registered_hemispheres_img_path = "registered_hemi.nii"

    with patch(
        "brainreg.core.backend.niftyreg.registration.safe_execute_command",
        side_effect=SafeExecuteCommandError("command failed"),
    ):
        with pytest.raises(SegmentationError):
            reg.register_hemispheres()
