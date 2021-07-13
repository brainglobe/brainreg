from napari_plugin_engine import napari_hook_implementation

from brainreg_napari.register import brainreg_register


@napari_hook_implementation
def napari_experimental_provide_dock_widget():
    return [(brainreg_register, {"name": "Atlas Registration"})]
