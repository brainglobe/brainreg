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
