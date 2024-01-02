from brainreg.napari.register import get_available_atlases

atlas_name = "allen_mouse_50um"


def test_get_available_atlases():
    atlases = get_available_atlases()

    # arbitrary selection of atlases
    expected_atlases = [
        "allen_mouse_10um",
        "allen_mouse_25um",
        "allen_mouse_50um",
        "mpin_zfish_1um",
    ]
    
    for a in expected_atlases:
        assert a in atlases.keys(), f"{a} is not in the list of expected atlases"
