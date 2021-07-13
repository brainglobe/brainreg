[![Python Version](https://img.shields.io/pypi/pyversions/brainreg-napari.svg)](https://pypi.org/project/brainreg-napari)
[![PyPI](https://img.shields.io/pypi/v/brainreg-napari.svg)](https://pypi.org/project/brainreg-napari)
[![Wheel](https://img.shields.io/pypi/wheel/brainreg-napari.svg)](https://pypi.org/project/brainreg-napari)
[![Development Status](https://img.shields.io/pypi/status/brainreg-napari.svg)](https://github.com/brainglobe/brainreg-napari)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/python/black)

# brainreg-napari
Napari plugin to run [brainreg](https://github.com/brainglobe/brainreg), 
developed by [Stephen Lenzi](https://github.com/stephenlenzi).

## Installation
```bash
pip install brainreg-napari
```

## Usage
Documentation for the plugin is to come, but documentation for the original 
brainreg can be found [here](https://docs.brainglobe.info/brainreg/introduction) 
and a tutorial is [here](https://docs.brainglobe.info/brainreg/tutorial). 

For segmentation of bulk structures in 3D space 
(e.g. injection sites, Neuropixels probes), please see 
[brainreg-segment](https://github.com/brainglobe/brainreg-segment).

This software is at a very early stage, and was written with our data in mind. 
Over time we hope to support other data types/formats. If you have any issues, please get in touch [on the forum](https://forum.image.sc/tag/brainglobe) or by 
[raising an issue](https://github.com/brainglobe/brainreg/issues). 

If you have any other questions, 
please send an [email](mailto:code@adamltyson.com?subject=brainreg).

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
![process](https://raw.githubusercontent.com/SainsburyWellcomeCentre/amap-python/master/resources/reg_process.png)
**Overview of the registration process**

### Citing brainreg

If you find brainreg useful, and use it in your research, please let us know and also cite the preprint:

> Tyson, A. L., V&eacute;lez-Fort, M.,  Rousseau, C. V., Cossell, L., Tsitoura, C., Obenhaus, H. A., Claudi, F., Lenzi, S. C., Branco, T.,  Margrie, T. W. (2021) “Tools for accurate post hoc determination of marker location within whole-brain microscopy images’ bioRxiv, [doi.org/10.1101/2021.05.21.445133](https://doi.org/10.1101/2021.05.21.445133)

Please also cite aMAP (the original pipeline from which this software is based):

>Niedworok, C.J., Brown, A.P.Y., Jorge Cardoso, M., Osten, P., Ourselin, S., Modat, M. and Margrie, T.W., (2016). AMAP is a validated pipeline for registration and segmentation of high-resolution mouse brain data. Nature Communications. 7, 1–9. https://doi.org/10.1038/ncomms11879

Lastly, if you can, please cite the BrainGlobe Atlas API that provided the atlas:

>Claudi, F., Petrucco, L., Tyson, A. L., Branco, T., Margrie, T. W. and Portugues, R. (2020). BrainGlobe Atlas API: a common interface for neuroanatomical atlases. Journal of Open Source Software, 5(54), 2668, https://doi.org/10.21105/joss.02668

**Don't forget to cite the developers of the atlas that you used (e.g. the Allen Brain Atlas)!**
