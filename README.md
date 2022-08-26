[![Python Version](https://img.shields.io/pypi/pyversions/brainreg.svg)](https://pypi.org/project/brainreg)
[![PyPI](https://img.shields.io/pypi/v/brainreg.svg)](https://pypi.org/project/brainreg)
[![Wheel](https://img.shields.io/pypi/wheel/brainreg.svg)](https://pypi.org/project/brainreg)
[![Development Status](https://img.shields.io/pypi/status/brainreg.svg)](https://github.com/brainglobe/brainreg)
[![Tests](https://img.shields.io/github/workflow/status/brainglobe/brainreg/tests)](
    https://github.com/brainglobe/brainreg/actions)
[![codecov](https://codecov.io/gh/brainglobe/brainreg/branch/master/graph/badge.svg?token=FbPgwBIGnd)](https://codecov.io/gh/brainglobe/brainreg)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/python/black)

# brainreg

brainreg is an update to
[amap](https://github.com/SainsburyWellcomeCentre/amap_python) (itself a port
of the [original Java software](https://www.nature.com/articles/ncomms11879))
to include multiple registration backends, and to support the many atlases
provided by [bg-atlasapi](https://github.com/brainglobe/bg-atlasapi).

Documentation can be found [here](https://docs.brainglobe.info/brainreg/introduction)
and a tutorial is [here](https://docs.brainglobe.info/brainreg/tutorial).
For segmentation of bulk structures in 3D space
(e.g. injection sites, Neuropixels probes), please see
[brainreg-segment](https://github.com/brainglobe/brainreg-segment).

**N.B. There is also a [napari plugin](https://github.com/brainglobe/brainreg-napari) if you'd rather use brainreg with a graphical user interface. Currently this interface is slightly limited compared to the command line tool**

This software is at a very early stage, and was written with our data in mind.
Over time we hope to support other data types/formats. If you have any issues, please get in touch [on the forum](https://forum.image.sc/tag/brainglobe) or by
[raising an issue](https://github.com/brainglobe/brainreg/issues).

## Details
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

## Installation
```bash
pip install brainreg
```

## Usage

### Basic usage
```bash
brainreg /path/to/raw/data /path/to/output/directory -v 5 2 2 --orientation psl
```

## Arguments
### Mandatory

* Path to the directory of the images. (Can also be a text file pointing to the files\)
* Output directory for all intermediate and final results

**You must also specify the voxel sizes, see [Specifying voxel size](https://docs.brainglobe.info/cellfinder/image-orientation#voxel-sizes)**

### Additional options

* `-a` or `--additional` Paths to N additional channels to downsample to the same coordinate space.
* `--sort-input-file` If set to true, the input text file will be sorted using natural sorting. This means that the file paths will be sorted as would be expected by a human and not purely alphabetically.
* `--brain_geometry` Can be one of `full` (default) for full brain registration, `hemisphere_l` for left hemisphere data-set and `hemisphere_r` for right hemisphere data-set.

#### Misc options

* `--n-free-cpus` The number of CPU cores on the machine to leave unused by the program to spare resources.
* `--debug` Debug mode. Will increase verbosity of logging and save all intermediate files for diagnosis of software issues.
* `--save-original-orientation` Option to save the registered atlas with the same orientation as the input data.

### Atlas

By default, brainreg will use the 25um version of the [Allen Mouse Brain Atlas](https://mouse.brain-map.org/). To use another atlas \(e.g. for another species, or another resolution\), you must use the `--atlas` flag, followed by the string describing the atlas, e.g.:

```bash
--atlas allen_mouse_50um
```

_To find out which atlases are available, once brainreg is installed, please run `brainglobe list`. The name of the resulting atlases is the string to pass with the `--atlas` flag._


### Registration backend

To change the registration algorithm used, use the `--backend` flag. The default is `niftyreg` as that is currently the only option.

### Input data orientation

If your data does not match the [brainglobe](https://github.com/brainglobe) default orientation \(the origin voxel is the most anterior, superior, left-most voxel, then you must specify the orientation by using the `--orientation` flag. What follows must be a string in the [bg-space](https://github.com/brainglobe/bg-space) "initials" form, to describe the origin voxel.



If the origin of your data \(first, top left voxel\) is the most anterior, superior, left part of the brain, then the orientation string would be "asl" \(anterior, superior, left\), and you would use:

```bash
--orientation asl
```


### Registration options

To change how the actual registration performs, see [Registration parameters](https://docs.brainglobe.info/brainreg/user-guide/parameters)

Full command-line arguments are available with `brainreg -h`, but please
[get in touch](mailto:adam.tyson@ucl.ac.uk?subject=brainreg) if you have any questions.


### Visualisation

brainreg comes with a plugin ([brainglobe-napari-io](https://github.com/brainglobe/brainglobe-napari-io)) for [napari](https://github.com/napari/napari) to view your data

##### Sample space
Open napari and drag your brainreg output directory (the one with the log file) onto the napari window.

Various images should then open, including:
* `Registered image` - the image used for registration, downsampled to atlas resolution
* `atlas_name` - e.g. `allen_mouse_25um` the atlas labels, warped to your sample brain
* `Boundaries` - the boundaries of the atlas regions

If you downsampled additional channels, these will also be loaded.

Most of these images will not be visible by default. Click the little eye icon to toggle visibility.

_N.B. If you use a high resolution atlas (such as `allen_mouse_10um`), then the files can take a little while to load._

![sample_space](https://raw.githubusercontent.com/brainglobe/napari-brainreg/master/resources/sample_space.gif)


##### Atlas space
`napari-brainreg` also comes with an additional plugin, for visualising your data
in atlas space.

This is typically only used in other software, but you can enable it yourself:
* Open napari
* Navigate to `Plugins` -> `Plugin Call Order`
* In the `Plugin Sorter` window, select `napari_get_reader` from the `select hook...` dropdown box
* Drag `brainreg_standard` (the atlas space viewer plugin) above `brainreg` (the normal plugin) to ensure that the atlas space plugin is used preferentially.

### Contributing
Contributions to brainreg are more than welcome. Please see the [contributing guide](https://github.com/brainglobe/.github/blob/main/CONTRIBUTING.md).

### Citing brainreg

If you find brainreg useful, and use it in your research, please let us know and also cite the paper:

> Tyson, A. L., V&eacute;lez-Fort, M.,  Rousseau, C. V., Cossell, L., Tsitoura, C., Lenzi, S. C., Obenhaus, H. A., Claudi, F., Branco, T.,  Margrie, T. W. (2022). Accurate determination of marker location within whole-brain microscopy images. Scientific Reports, 12, 867 [doi.org/10.1038/s41598-021-04676-9](https://doi.org/10.1038/s41598-021-04676-9)

Please also cite aMAP (the original pipeline from which this software is based):

>Niedworok, C.J., Brown, A.P.Y., Jorge Cardoso, M., Osten, P., Ourselin, S., Modat, M. and Margrie, T.W., (2016). AMAP is a validated pipeline for registration and segmentation of high-resolution mouse brain data. Nature Communications. 7, 1–9. https://doi.org/10.1038/ncomms11879

Lastly, if you can, please cite the BrainGlobe Atlas API that provided the atlas:

>Claudi, F., Petrucco, L., Tyson, A. L., Branco, T., Margrie, T. W. and Portugues, R. (2020). BrainGlobe Atlas API: a common interface for neuroanatomical atlases. Journal of Open Source Software, 5(54), 2668, https://doi.org/10.21105/joss.02668

**Don't forget to cite the developers of the atlas that you used (e.g. the Allen Brain Atlas)!**



---
The BrainGlobe project is generously supported by the Sainsbury Wellcome Centre and the Institute of Neuroscience, Technical University of Munich, with funding from Wellcome, the Gatsby Charitable Foundation and the Munich Cluster for Systems Neurology - Synergy.

<img src='https://brainglobe.info/images/logos_combined.png' width="550">
