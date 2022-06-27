import napari
import pytest

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


def test_add_layers_errors(tmp_path, make_napari_viewer):
    """
    Check that an error is raised if registration metadata isn't present when
    trying to add registered images to a napari viewer.
    """
    viewer = make_napari_viewer()
    with pytest.raises(FileNotFoundError):
        add_registered_image_layers(viewer, registration_directory=tmp_path)
