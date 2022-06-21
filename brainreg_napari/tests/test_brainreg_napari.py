import napari

from brainreg_napari.register import brainreg_register


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

    # Run registration
    widget(block=True)
