"""
Load and show sample data
=========================
This example:
- loads some sample data
- adds the data to a napari viewer
- loads the brainreg-napari registration plugin
- opens the napari viewer
"""
import numpy as np
import napari
from napari.layers import Layer

from brainreg_napari.sample_data import load_test_brain

viewer = napari.Viewer()

layer_data = load_test_brain()[0]
# Set sensible contrast limits for viewing the brain
layer_data[1]['contrast_limits'] = np.percentile(layer_data[0], [0, 99.5])
# Add data to napari
viewer.add_layer(Layer.create(*layer_data))

# Open plugin
_, brainreg_widget = viewer.window.add_plugin_dock_widget(
    plugin_name="brainreg-napari", widget_name="Atlas Registration"
)
# Set brainreg-napari plugin settings from sample data metadata
metadata = layer_data[1]["metadata"]
brainreg_widget.data_orientation.value = metadata["data_orientation"]
for i, dim in enumerate(["z", "y", "x"]):
    pixel_widget = getattr(brainreg_widget, f"{dim}_pixel_um")
    pixel_widget.value = metadata["voxel_size"][i]


if __name__ == "__main__":
    # The napari event loop needs to be run under here to allow the window
    # to be spawned from a Python script
    napari.run()
