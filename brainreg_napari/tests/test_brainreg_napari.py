from brainreg_napari.register import brainreg_register


def test_add_detect_widget(make_napari_viewer):
    """
    Smoke test to check that adding detection widget works
    """
    viewer = make_napari_viewer()
    widget = brainreg_register()
    viewer.window.add_dock_widget(widget)
