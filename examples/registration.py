"""
Load and show sample data
=========================
This example:
- loads some sample data
- adds the data to a napari viewer
- loads the brainreg-napari cell detection plugin
- opens the napari viewer
"""
import napari

from brainreg_napari.sample_data import load_sample

viewer = napari.Viewer()
# Open plugin
viewer.window.add_plugin_dock_widget(
    plugin_name="brainreg-napari", widget_name="Atlas Registration"
)
# Add sample data layers
for layer in load_sample():
    viewer.add_layer(napari.layers.Image(layer[0], **layer[1]))


if __name__ == "__main__":
    # The napari event loop needs to be run under here to allow the window
    # to be spawned from a Python script
    napari.run()
