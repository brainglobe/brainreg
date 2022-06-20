from brainreg_napari.register import brainreg_register
from brainreg_napari.sample_data import load_test_brain


def test_add_detect_widget(make_napari_viewer):
    """
    Smoke test to check that adding detection widget works
    """
    viewer = make_napari_viewer()
    widget = brainreg_register()
    viewer.window.add_dock_widget(widget)


def test_get_sample_data():
    """
    Check that fetching the test brain works.
    """
    layer_data_list = load_test_brain()
    layer_data = layer_data_list[0]
    assert layer_data[0].shape == (270, 193, 271)
    assert layer_data[2] == "image"
