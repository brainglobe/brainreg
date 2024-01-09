[![Python Version](https://img.shields.io/pypi/pyversions/brainreg.svg)](https://pypi.org/project/brainreg)
[![PyPI](https://img.shields.io/pypi/v/brainreg.svg)](https://pypi.org/project/brainreg)
[![Wheel](https://img.shields.io/pypi/wheel/brainreg.svg)](https://pypi.org/project/brainreg)
[![Development Status](https://img.shields.io/pypi/status/brainreg.svg)](https://github.com/brainglobe/brainreg)
[![Tests](https://img.shields.io/github/actions/workflow/status/brainglobe/brainreg/test_and_deploy.yml?branch=main)](https://github.com/brainglobe/brainreg/actions)
[![codecov](https://codecov.io/gh/brainglobe/brainreg/branch/master/graph/badge.svg?token=FbPgwBIGnd)](https://codecov.io/gh/brainglobe/brainreg)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/python/black)

# brainreg

brainreg is an update to [amap](https://github.com/SainsburyWellcomeCentre/amap_python) (which is itself a port
of the [original Java software](https://www.nature.com/articles/ncomms11879)) to include multiple registration backends, and to support the many atlases provided by [bg-atlasapi](https://github.com/brainglobe/bg-atlasapi).
It also comes with an optional [napari plugin](https://github.com/brainglobe/brainreg-napari) if you'd rather use brainreg with through graphical interface.

Documentation for both the command-line tool and graphical interface can be found [here](https://brainglobe.info/documentation/brainreg/index.html).
If you have any issues, please get in touch [on the forum](https://forum.image.sc/tag/brainglobe), [on Zulip](https://brainglobe.zulipchat.com/), or by
[raising an issue](https://github.com/brainglobe/brainreg/issues).

For segmentation of bulk structures in 3D space (e.g. injection sites, Neuropixels probes), please see [brainglobe-segmentation](https://github.com/brainglobe/brainglobe-segmentation).

## Details

The aim of brainreg is to register the template brain (e.g. from the [Allen Reference Atlas](https://mouse.brain-map.org/static/atlas)) to the sample image.
Once this is complete, any other image in the template space can be aligned with the sample (such as region annotations, for segmentation of the sample image).
The template to sample transformation can also be inverted, allowing sample images to be aligned in a common coordinate space.

To do this, the template and sample images are filtered, and then registered in a three step process (reorientation, affine registration, and freeform registration).
The resulting transform from template to standard space is then applied to the atlas.

Full details of the process are in the [original aMAP paper](https://www.nature.com/articles/ncomms11879).

![An illustrated overview of the registration process](https://user-images.githubusercontent.com/13147259/143553945-a046e918-7614-4211-814c-fc840bb0159d.png)

## Installation

To install both the command line tool and the napari plugin, run

```bash
pip install brainreg[napari]
```

in your desired Python environment.
To only install the command line tool with no GUI (e.g. to run brainreg on an HPC cluster), just run:

```bash
pip install brainreg
```

### Installing on macOS

If you are using macOS, please run

```bash
conda install -c conda-forge niftyreg
```

in your environment before installing, to ensure all dependencies are installed.

## Command line usage

### Basic usage

```bash
brainreg /path/to/raw/data /path/to/output/directory -v 5 2 2 --orientation psl
```

Full command-line arguments are available with `brainreg -h`, but please
[get in touch](mailto:code@adamltyson.com?subject=brainreg) if you have any questions.

### Mandatory arguments

- Path to the directory of the images. This can also be a text file pointing to the files.
- Output directory for all intermediate and final results.
- You must also specify the voxel sizes with the `-v` flag, see [specifying voxel size](https://brainglobe.info/documentation/general/image-definition.html#voxel-sizes) for details.

### Atlas

By default, brainreg will use the 25um version of the [Allen Mouse Brain Atlas](https://mouse.brain-map.org/).
To use another atlas (e.g. for another species, or another resolution), you must use the `--atlas` flag, followed by the string describing the atlas, e.g.:

```bash
--atlas allen_mouse_50um
```

To find out which atlases are available, once brainreg is installed, please run `brainglobe list`.
The name of the resulting atlases is the string to pass with the `--atlas` flag.

### Input data orientation

If your data does not match the BrainGlobe default orientation (the origin voxel is the most anterior, superior, left-most voxel), then you must specify the orientation by using the `--orientation` flag.
What follows must be a string in the [bg-space](https://github.com/brainglobe/bg-space) "initials" form, to describe the origin voxel.

If the origin of your data (first, top left voxel) is the most anterior, superior, left part of the brain, then the orientation string would be "asl" (anterior, superior, left), and you would use:

```bash
--orientation asl
```

### Registration options

To change how the actual registration performs, see [registration parameters](https://brainglobe.info/documentation/brainreg/user-guide/parameters.html)

### Additional options

- `-a` or `--additional` Paths to N additional channels to downsample to the same coordinate space.
- `--sort-input-file` If set to true, the input text file will be sorted using natural sorting. This means that the file paths will be sorted as would be expected by a human and not purely alphabetically.
- `--brain_geometry` Can be one of `full` (default) for full brain registration, `hemisphere_l` for left hemisphere data-set and `hemisphere_r` for right hemisphere data-set.

### Misc options

- `--n-free-cpus` The number of CPU cores on the machine to leave unused by the program to spare resources.
- `--debug` Debug mode. Will increase verbosity of logging and save all intermediate files for diagnosis of software issues.
- `--save-original-orientation` Option to save the registered atlas with the same orientation as the input data.

## Visualising results

If you have installed the optional [napari](https://github.com/napari/napari) plugin, you can use napari to view your data.
The plugin automatically fetches the [brainglobe-napari-io](https://github.com/brainglobe/brainglobe-napari-io) which provides this functionality.
If you have installed only the command-line tool you can still manually install [brainglobe-napari-io](https://github.com/brainglobe/brainglobe-napari-io) and follow the steps below.

### Sample space

Open napari and drag your brainreg output directory (the one with the log file) onto the napari window.

Various images should then open, including:

- `Registered image` - the image used for registration, downsampled to atlas resolution
- `atlas_name` - e.g. `allen_mouse_25um` the atlas labels, warped to your sample brain
- `Boundaries` - the boundaries of the atlas regions

If you downsampled additional channels, these will also be loaded.
Most of these images will not be visible by default - click the little eye icon to toggle visibility.

**Note:** If you use a high resolution atlas (such as `allen_mouse_10um`), then the files can take a little while to load.

![GIF illustration of loading brainreg output into napari for visualisation](https://raw.githubusercontent.com/brainglobe/napari-brainreg/master/resources/sample_space.gif)

## Contributing

Contributions to brainreg are more than welcome.
Please see the [developers guide](https://brainglobe.info/developers/index.html).

## Citing brainreg

If you find brainreg useful, and use it in your research, please let us know and also cite the paper:

> Tyson, A. L., V&eacute;lez-Fort, M.,  Rousseau, C. V., Cossell, L., Tsitoura, C., Lenzi, S. C., Obenhaus, H. A., Claudi, F., Branco, T.,  Margrie, T. W. (2022). Accurate determination of marker location within whole-brain microscopy images. Scientific Reports, 12, 867 [doi.org/10.1038/s41598-021-04676-9](https://doi.org/10.1038/s41598-021-04676-9)

Please also cite aMAP (the original pipeline from which this software is based):

>Niedworok, C.J., Brown, A.P.Y., Jorge Cardoso, M., Osten, P., Ourselin, S., Modat, M. and Margrie, T.W., (2016). AMAP is a validated pipeline for registration and segmentation of high-resolution mouse brain data. Nature Communications. 7, 1–9. <https://doi.org/10.1038/ncomms11879>

Lastly, if you can, please cite the BrainGlobe Atlas API that provided the atlas:

>Claudi, F., Petrucco, L., Tyson, A. L., Branco, T., Margrie, T. W. and Portugues, R. (2020). BrainGlobe Atlas API: a common interface for neuroanatomical atlases. Journal of Open Source Software, 5(54), 2668, <https://doi.org/10.21105/joss.02668>

Finally, **don't forget to cite the developers of the atlas that you used (e.g. the Allen Brain Atlas)!**
