from brainreg_napari.register import register
from napari_plugin_engine import napari_hook_implementation


@napari_hook_implementation
def napari_experimental_provide_dock_widget():
    return [(register, {"name": "register"})]
