from brainreg.napari.register import get_available_atlases

atlas_name = "allen_mouse_50um"


def test_get_available_atlases():
    atlases = get_available_atlases()

    # arbitrary selection of atlases
    assert float(atlases["allen_mouse_10um"]) >= 0.3
    assert float(atlases["allen_mouse_25um"]) >= 0.3
    assert float(atlases["allen_mouse_50um"]) >= 0.3
    assert float(atlases["mpin_zfish_1um"]) >= 0.4