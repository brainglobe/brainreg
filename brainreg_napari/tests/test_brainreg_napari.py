import napari
import pytest
from bg_atlasapi import BrainGlobeAtlas

from brainreg_napari.register import (
    add_registered_image_layers,
    brainreg_register,
)


def test_add_detect_widget(make_napari_viewer):
    """
    Smoke test to check that adding detection widget works
    """
    viewer = make_napari_viewer()
    widget = brainreg_register()
    viewer.window.add_dock_widget(widget)


def test_napari_sample_data(make_napari_viewer):
    """
    Check that loading the sample data via napari works.
    """
    viewer = make_napari_viewer()

    assert len(viewer.layers) == 0
    viewer.open_sample("brainreg-napari", "sample")
    assert len(viewer.layers) == 1
    new_layer = viewer.layers[0]
    assert isinstance(new_layer, napari.layers.Image)
    assert new_layer.data.shape == (270, 193, 271)


def test_workflow(make_napari_viewer, tmp_path):
    """
    Test a full workflow using brainreg-napari.
    """
    viewer = make_napari_viewer()

    # Load sample data
    added_layers = viewer.open_sample("brainreg-napari", "sample")
    brain_layer = added_layers[0]

    # Load widget
    _, widget = viewer.window.add_plugin_dock_widget(
        plugin_name="brainreg-napari", widget_name="Atlas Registration"
    )
    # Set active layer and output folder
    widget.img_layer.value = brain_layer
    widget.registration_output_folder.value = tmp_path

    # Set widget settings from brain data metadata
    widget.data_orientation.value = brain_layer.metadata["data_orientation"]
    for i, dim in enumerate(["z", "y", "x"]):
        pixel_widget = getattr(widget, f"{dim}_pixel_um")
        pixel_widget.value = brain_layer.metadata["voxel_size"][i]

    assert len(viewer.layers) == 1

    # Run registration
    widget(block=True)

    # Check that layers have been added
    assert len(viewer.layers) == 3
    # Check layers have expected type/name
    labels = viewer.layers[1]
    assert isinstance(labels, napari.layers.Labels)
    assert labels.name == "example_mouse_100um"
    for key in ["orientation", "atlas"]:
        # There are lots of other keys in the metadata, but just check
        # for a couple here.
        assert (
            key in labels.metadata
        ), f"Missing key '{key}' from labels metadata"

    boundaries = viewer.layers[2]
    assert isinstance(boundaries, napari.layers.Image)
    assert boundaries.name == "Boundaries"


def test_orientation_check(
    make_napari_viewer, tmp_path, atlas_choice="allen_mouse_50um"
):
    """
    Test that the check orientation function works
    """
    viewer = make_napari_viewer()

    # Load widget
    _, widget = viewer.window.add_plugin_dock_widget(
        plugin_name="brainreg-napari", widget_name="Atlas Registration"
    )

    # Set a specific atlas
    # Should be a better way of doing this
    for choice in widget.atlas_key.choices:
        if choice.name == atlas_choice:
            widget.atlas_key.value = choice
            break

    assert widget.atlas_key.value.name == atlas_choice

    widget.check_orientation_button.clicked()
    assert len(viewer.layers) == 0

    # Load sample data
    added_layers = viewer.open_sample("brainreg-napari", "sample")
    brain_layer = added_layers[0]

    assert len(viewer.layers) == 1

    atlas = BrainGlobeAtlas(atlas_choice)
    # click check orientation button and check output
    run_and_check_orientation_check(widget, viewer, brain_layer, atlas)

    # run again and check previous output was deleted properly
    run_and_check_orientation_check(widget, viewer, brain_layer, atlas)


def run_and_check_orientation_check(widget, viewer, brain_layer, atlas):
    widget.check_orientation_button.clicked()
    check_orientation_output(viewer, brain_layer, atlas)


def check_orientation_output(viewer, brain_layer, atlas):
    # 1 for the loaded data, and three each for the
    # views of two images (data & atlas)
    assert len(viewer.layers) == 7
    assert brain_layer.visible is False
    for i in range(1, 7):
        layer = viewer.layers[i]
        assert isinstance(layer, napari.layers.Image)
        assert layer.visible is True
        assert layer.ndim == 2

    assert viewer.layers[4].data.shape == (
        brain_layer.data.shape[1],
        brain_layer.data.shape[2],
    )
    assert viewer.layers[5].data.shape == (
        brain_layer.data.shape[0],
        brain_layer.data.shape[2],
    )
    assert viewer.layers[6].data.shape == (
        brain_layer.data.shape[0],
        brain_layer.data.shape[1],
    )

    assert viewer.layers[1].data.shape == (atlas.shape[1], atlas.shape[2])
    assert viewer.layers[2].data.shape == (atlas.shape[0], atlas.shape[2])
    assert viewer.layers[3].data.shape == (atlas.shape[0], atlas.shape[1])


def test_add_layers_errors(tmp_path, make_napari_viewer):
    """
    Check that an error is raised if registration metadata isn't present when
    trying to add registered images to a napari viewer.
    """
    viewer = make_napari_viewer()
    with pytest.raises(FileNotFoundError):
        add_registered_image_layers(viewer, registration_directory=tmp_path)
