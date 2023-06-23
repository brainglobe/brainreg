[![Python Version](https://img.shields.io/pypi/pyversions/brainreg-napari.svg)](https://pypi.org/project/brainreg-napari)
[![PyPI](https://img.shields.io/pypi/v/brainreg-napari.svg)](https://pypi.org/project/brainreg-napari)
[![Wheel](https://img.shields.io/pypi/wheel/brainreg-napari.svg)](https://pypi.org/project/brainreg-napari)
[![Development Status](https://img.shields.io/pypi/status/brainreg-napari.svg)](https://github.com/brainglobe/brainreg-napari)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/python/black)
[![codecov](https://codecov.io/gh/brainglobe/brainreg-napari/branch/master/graph/badge.svg?token=HEBXJPLD2S)](https://codecov.io/gh/brainglobe/brainreg-napari)

# brainreg-napari
Napari plugin to run [brainreg](https://github.com/brainglobe/brainreg),
developed by [Stephen Lenzi](https://github.com/stephenlenzi).

## Installation
```bash
pip install brainreg-napari
```

## Usage
Documentation and tutorials for the plugin can be found [here](https://brainglobe.info/documentation/brainreg/index.html).

For segmentation of bulk structures in 3D space
(e.g. injection sites, Neuropixels probes), please see
[brainreg-segment](https://github.com/brainglobe/brainreg-segment).

This software is at a very early stage, and was written with our data in mind.
Over time we hope to support other data types/formats. If you have any issues, please get in touch [on the forum](https://forum.image.sc/tag/brainglobe) or by
[raising an issue](https://github.com/brainglobe/brainreg/issues).

## Details
brainreg is an update to
[amap](https://github.com/SainsburyWellcomeCentre/amap-python) (itself a port
of the [original Java software](https://www.nature.com/articles/ncomms11879))
to include multiple registration backends, and to support the many atlases
provided by [bg-atlasapi](https://github.com/brainglobe/bg-atlasapi).

The aim of brainreg is to register the template brain
 (e.g. from the [Allen Reference Atlas](https://mouse.brain-map.org/static/atlas))
  to the sample image. Once this is complete, any other image in the template
  space can be aligned with the sample (such as region annotations, for
  segmentation of the sample image). The template to sample transformation
  can also be inverted, allowing sample images to be aligned in a common
  coordinate space.

To do this, the template and sample images are filtered, and then registered in
a three step process (reorientation, affine registration, and freeform
registration.) The resulting transform from template to standard space is then
applied to the atlas.

Full details of the process are in the
[original aMAP paper](https://www.nature.com/articles/ncomms11879).
![reg_process](https://user-images.githubusercontent.com/13147259/143553945-a046e918-7614-4211-814c-fc840bb0159d.png)
**Overview of the registration process**

## Contributing
Contributions to brainreg-napari are more than welcome. Please see the [developers guide](https://brainglobe.info/developers/index.html).

### Citing brainreg

If you find brainreg useful, and use it in your research, please let us know and also cite the paper:

> Tyson, A. L., V&eacute;lez-Fort, M.,  Rousseau, C. V., Cossell, L., Tsitoura, C., Lenzi, S. C., Obenhaus, H. A., Claudi, F., Branco, T.,  Margrie, T. W. (2022). Accurate determination of marker location within whole-brain microscopy images. Scientific Reports, 12, 867 [doi.org/10.1038/s41598-021-04676-9](https://doi.org/10.1038/s41598-021-04676-9)

Please also cite aMAP (the original pipeline from which this software is based):

>Niedworok, C.J., Brown, A.P.Y., Jorge Cardoso, M., Osten, P., Ourselin, S., Modat, M. and Margrie, T.W., (2016). AMAP is a validated pipeline for registration and segmentation of high-resolution mouse brain data. Nature Communications. 7, 1–9. https://doi.org/10.1038/ncomms11879

Lastly, if you can, please cite the BrainGlobe Atlas API that provided the atlas:

>Claudi, F., Petrucco, L., Tyson, A. L., Branco, T., Margrie, T. W. and Portugues, R. (2020). BrainGlobe Atlas API: a common interface for neuroanatomical atlases. Journal of Open Source Software, 5(54), 2668, https://doi.org/10.21105/joss.02668

**Don't forget to cite the developers of the atlas that you used (e.g. the Allen Brain Atlas)!**
