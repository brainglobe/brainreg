[![Python Version](https://img.shields.io/pypi/pyversions/brainreg.svg)](https://pypi.org/project/amap)
[![PyPI](https://img.shields.io/pypi/v/brainreg.svg)](https://pypi.org/project/brainreg)
[![Wheel](https://img.shields.io/pypi/wheel/brainreg.svg)](https://pypi.org/project/brainreg)
[![Development Status](https://img.shields.io/pypi/status/brainreg.svg)](https://github.com/brainglobe/brainreg)
[![Travis](https://img.shields.io/travis/com/brainglobe/brainreg?label=Travis%20CI)](
    https://travis-ci.com/brainglobe/brainreg)
[![Coverage Status](https://coveralls.io/repos/github/brainglobe/brainreg/badge.svg?branch=master)](https://coveralls.io/github/brainglobe/brainreg?branch=master)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/python/black)
[![DOI](https://zenodo.org/badge/267067901.svg)](https://zenodo.org/badge/latestdoi/267067901)
[![Gitter](https://badges.gitter.im/cellfinder/brainreg.svg)](https://gitter.im/cellfinder/brainreg?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge)

# brainreg

brainreg is an update to 
[amap](https://github.com/SainsburyWellcomeCentre/amap-python) (itself a port 
of the [original Java software](https://www.nature.com/articles/ncomms11879)) 
to include multiple registration backends, and to support the many atlases 
provided by [bg-atlasapi](https://github.com/brainglobe/bg-atlasapi).

Documentation can be found [here](https://docs.brainglobe.info/brainreg/introduction) 
and a tutorial is [here](https://docs.brainglobe.info/brainreg/tutorial).

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
![process](https://raw.githubusercontent.com/SainsburyWellcomeCentre/amap-python/master/resources/reg_process.png)
**Overview of the registration process**

## Installation
```bash
pip install brainreg
```

## Usage

### Basic usage
```bash
brainreg /path/to/raw/data /path/to/output/directory -x 2 -y 2 -z 5
```

## Arguments
### Mandatory

* Path to the directory of the images. (Can also be a text file pointing to the files\)
* Output directory for all intermediate and final results

**You must also specify the pixel sizes, see [Specifying pixel size](https://docs.cellfinder.info/user-guide/usage/specifying-pixel-size)**

### Additional options

* `-d` or `--downsample` Paths to N additional channels to downsample to the same coordinate space.
* `--sort-input-file` If set to true, the input text file will be sorted using natural sorting. This means that the file paths will be sorted as would be expected by a human and not purely alphabetically

#### Misc options

* `--n-free-cpus` The number of CPU cores on the machine to leave unused by the program to spare resources.
* `--debug` Debug mode. Will increase verbosity of logging and save all intermediate files for diagnosis of software issues.

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

To change how the actual registration performs, see [Registration parameters](https://docs.cellfinder.info/brainreg/getting-started/registration-parameters)

Full command-line arguments are available with `brainreg -h`, but please 
[get in touch](mailto:adam.tyson@ucl.ac.uk?subject=brainreg) if you have any questions.


### Visualisation

brainreg comes with a plugin ([napari-brainreg](https://github.com/brainglobe/napari-brainreg)) for [napari](https://github.com/napari/napari) to view your data

##### Sample space
Open napari and drag your [brainreg](https://github.com/brainglobe/brainreg) output directory (the one with the log file) onto the napari window.
    
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

![atlas_space](https://raw.githubusercontent.com/brainglobe/napari-brainreg/master/resources/atlas_space.gif)

### Citing brainreg

If you find brainreg useful, and use it in your research, please let us know and also cite this repository:

> Adam L. Tyson, Charly V. Rousseau, and Troy W. Margrie (2020). brainreg: automated 3D brain registration with support for multiple species and atlases. [10.5281/zenodo.3991718](https://doi.org/10.5281/zenodo.3991718)