from pathlib import Path

import pytest

from brainreg.core.cli import prep_registration


def test_prep_registration_different_names(mocker):
    """Check that additional channel names are returned, when unique."""
    args = mocker.Mock()
    args.brainreg_directory = Path.home()  # This just needs to exist
    args.additional_images = [
        Path.home() / "additional_channel_0",
        Path.home() / "additional_channel_1",
    ]

    _, additional_channel_outputs = prep_registration(args)
    assert "additional_channel_0" in additional_channel_outputs
    assert "additional_channel_1" in additional_channel_outputs


def test_additional_channels_same_name_different_parent_name(mocker):
    """
    Check that parent folder name returned if additional channel names are not unique.
    """
    args = mocker.Mock()
    args.brainreg_directory = Path.home()  # This just needs to exist
    args.additional_images = [
        Path.home() / "folder_0/duplicate_name",
        Path.home() / "folder_1/duplicate_name",
    ]

    _, additional_channel_outputs = prep_registration(args)
    assert "folder_1_duplicate_name" in additional_channel_outputs
    assert "folder_1_duplicate_name" in additional_channel_outputs


def test_prep_registration_same_name_same_parent_name(mocker):
    """Check that error is thrown if both parent and additional channel name are non-unique."""
    args = mocker.Mock()
    args.brainreg_directory = Path.home()  # This just needs to exist
    args.additional_images = [
        str(Path.home() / "duplicate_name"),
        str(Path.home() / "duplicate_name"),
    ]

    with pytest.raises(
        AssertionError,
        match=".*ensure additional channels have a unique combination of name and parent folder.*",
    ):
        prep_registration(args)
