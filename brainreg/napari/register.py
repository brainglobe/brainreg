import json
import logging
import pathlib
from collections import namedtuple
from enum import Enum
from typing import Dict, List, Tuple

import bg_space as bg
import napari
import numpy as np
from bg_atlasapi import BrainGlobeAtlas
from bg_atlasapi.list_atlases import descriptors, utils
from brainglobe_napari_io.brainmapper.brainmapper_reader_dir import (
    load_registration,
)
from fancylog import fancylog
from magicgui import magicgui
from napari._qt.qthreading import thread_worker
from napari.types import LayerDataTuple
from napari.utils.notifications import show_info

import brainreg as program_for_log
from brainreg.core.backend.niftyreg.run import run_niftyreg
from brainreg.core.paths import Paths
from brainreg.core.utils.boundaries import boundaries
from brainreg.core.utils.misc import log_metadata
from brainreg.core.utils.volume import calculate_volumes
from brainreg.napari.util import (
    NiftyregArgs,
    downsample_and_save_brain,
    initialise_brainreg,
)

PRE_PROCESSING_ARGS = None


def get_available_atlases():
    """
    Get the available brainglobe atlases
    :return: Dict of available atlases (["name":version])
    """
    available_atlases = utils.conf_from_url(
        descriptors.remote_url_base.format("last_versions.conf")
    )
    available_atlases = dict(available_atlases["atlases"])
    return available_atlases


def add_registered_image_layers(
    viewer: napari.Viewer, *, registration_directory: pathlib.Path
) -> Tuple[napari.layers.Image, napari.layers.Labels]:
    """
    Read in saved registration data and add as layers to the
    napari viewer.

    Returns
    -------
    boundaries :
        Registered boundaries.
    labels :
        Registered brain regions.
    """
    layers: List[LayerDataTuple] = []

    meta_file = (registration_directory / "brainreg.json").resolve()
    if meta_file.exists():
        with open(meta_file) as json_file:
            metadata = json.load(json_file)
        layers = load_registration(layers, registration_directory, metadata)
    else:
        raise FileNotFoundError(
            f"'brainreg.json' file not found in {registration_directory}"
        )

    boundaries = viewer.add_layer(napari.layers.Layer.create(*layers[0]))
    labels = viewer.add_layer(napari.layers.Layer.create(*layers[1]))
    return boundaries, labels


def get_layer_labels(widget):
    return [layer._name for layer in widget.viewer.value.layers]


def get_additional_images_downsample(widget) -> Dict[str, str]:
    """
    For any selected layers loaded from a file, get a mapping from
    layer name -> layer file path.
    """
    images = {}
    for layer in widget.viewer.value.layers.selection:
        if layer._source.path is not None:
            images[layer._name] = str(layer._source.path)
    return images


def get_atlas_dropdown():
    atlas_dict = {}
    for i, k in enumerate(get_available_atlases().keys()):
        atlas_dict.setdefault(k, k)
    atlas_keys = Enum("atlas_key", atlas_dict)
    return atlas_keys


def get_brain_geometry_dropdown():
    geometry_dict = {
        "Full brain": "full",
        "Right hemisphere": "hemisphere_r",
        "Left hemisphere": "hemisphere_l",
    }
    return Enum("geometry_keys", geometry_dict)


def brainreg_register():
    DEFAULT_PARAMETERS = dict(
        z_pixel_um=5,
        y_pixel_um=2,
        x_pixel_um=2,
        data_orientation="psl",
        brain_geometry=get_brain_geometry_dropdown(),
        save_original_orientation=False,
        atlas_key=get_atlas_dropdown(),
        registration_output_folder=pathlib.Path.home(),
        affine_n_steps=6,
        affine_use_n_steps=5,
        freeform_n_steps=6,
        freeform_use_n_steps=4,
        bending_energy_weight=0.95,
        grid_spacing=10,
        smoothing_sigma_reference=1,
        smoothing_sigma_floating=1,
        histogram_n_bins_floating=128,
        histogram_n_bins_reference=128,
        debug=False,
    )

    @magicgui(
        call_button=True,
        img_layer=dict(
            label="Image layer",
        ),
        atlas_key=dict(
            label="Atlas",
        ),
        z_pixel_um=dict(
            value=DEFAULT_PARAMETERS["z_pixel_um"],
            label="Voxel size (z)",
            step=0.1,
        ),
        y_pixel_um=dict(
            value=DEFAULT_PARAMETERS["y_pixel_um"],
            label="Voxel size (y)",
            step=0.1,
        ),
        x_pixel_um=dict(
            value=DEFAULT_PARAMETERS["x_pixel_um"],
            label="Voxel size (x)",
            step=0.1,
        ),
        data_orientation=dict(
            value=DEFAULT_PARAMETERS["data_orientation"],
            label="Data orientation",
        ),
        brain_geometry=dict(
            label="Brain geometry",
        ),
        registration_output_folder=dict(
            value=DEFAULT_PARAMETERS["registration_output_folder"],
            mode="d",
            label="Output directory",
        ),
        save_original_orientation=dict(
            value=DEFAULT_PARAMETERS["save_original_orientation"],
            label="Save original orientation",
        ),
        affine_n_steps=dict(
            value=DEFAULT_PARAMETERS["affine_n_steps"], label="affine_n_steps"
        ),
        affine_use_n_steps=dict(
            value=DEFAULT_PARAMETERS["affine_use_n_steps"],
            label="affine_use_n_steps",
        ),
        freeform_n_steps=dict(
            value=DEFAULT_PARAMETERS["freeform_n_steps"],
            label="freeform_n_steps",
        ),
        freeform_use_n_steps=dict(
            value=DEFAULT_PARAMETERS["freeform_use_n_steps"],
            label="freeform_use_n_steps",
        ),
        bending_energy_weight=dict(
            value=DEFAULT_PARAMETERS["bending_energy_weight"],
            label="bending_energy_weight",
        ),
        grid_spacing=dict(
            value=DEFAULT_PARAMETERS["grid_spacing"], label="grid_spacing"
        ),
        smoothing_sigma_reference=dict(
            value=DEFAULT_PARAMETERS["smoothing_sigma_reference"],
            label="smoothing_sigma_reference",
        ),
        smoothing_sigma_floating=dict(
            value=DEFAULT_PARAMETERS["smoothing_sigma_floating"],
            label="smoothing_sigma_floating",
        ),
        histogram_n_bins_floating=dict(
            value=DEFAULT_PARAMETERS["histogram_n_bins_floating"],
            label="histogram_n_bins_floating",
        ),
        histogram_n_bins_reference=dict(
            value=DEFAULT_PARAMETERS["histogram_n_bins_reference"],
            label="histogram_n_bins_reference",
        ),
        debug=dict(
            value=DEFAULT_PARAMETERS["debug"],
            label="Debug mode",
        ),
        reset_button=dict(widget_type="PushButton", text="Reset defaults"),
        check_orientation_button=dict(
            widget_type="PushButton", text="Check orientation"
        ),
    )
    def widget(
        viewer: napari.Viewer,
        img_layer: napari.layers.Image,
        atlas_key: get_atlas_dropdown(),
        data_orientation: str,
        brain_geometry: get_brain_geometry_dropdown(),
        z_pixel_um: float,
        x_pixel_um: float,
        y_pixel_um: float,
        registration_output_folder: pathlib.Path,
        save_original_orientation: bool,
        affine_n_steps: int,
        affine_use_n_steps: int,
        freeform_n_steps: int,
        freeform_use_n_steps: int,
        bending_energy_weight: float,
        grid_spacing: int,
        smoothing_sigma_reference: int,
        smoothing_sigma_floating: float,
        histogram_n_bins_floating: float,
        histogram_n_bins_reference: float,
        debug: bool,
        reset_button,
        check_orientation_button,
        block: bool = False,
    ):
        """
        Parameters
        ----------
        img_layer : napari.layers.Image
             Image layer to be registered
        atlas_key : str
             Atlas to use for registration
        data_orientation: str
            Three characters describing the data orientation, e.g. "psl".
            See docs for more details.
        brain_geometry: str
            To allow brain sub-volumes to be processed. Choose whether your
            data is a whole brain or a single hemisphere.
        z_pixel_um : float
            Size of your voxels in the axial dimension
        y_pixel_um : float
            Size of your voxels in the y direction (top to bottom)
        x_pixel_um : float
            Size of your voxels in the xdirection (left to right)
        registration_output_folder: pathlib.Path
            Where to save the registration output
                affine_n_steps: int,
        save_original_orientation: bool
            Option to save annotations with the same orientation as the input
             data. Use this if you plan to map
            segmented objects outside brainglobe/tools.
        affine_n_steps: int
             Registration starts with further downsampled versions of the
             original data to optimize the global fit of the result and
             prevent "getting stuck" in local minima of the similarity
             function. This parameter determines how many downsampling steps
             are being performed, with each step halving the data size along
             each dimension.
        affine_use_n_steps: int
             Determines how many of the downsampling steps defined by
             affine-_n_steps will have their registration computed. The
              combination affine_n_steps=3, affine_use_n_steps=2 will e.g.
              calculate 3 downsampled steps, each of which is half the size
              of the previous one but only perform the registration on the
              2 smallest resampling steps, skipping the full resolution data.
               Can be used to save time if running the full resolution doesn't
               result in noticeable improvements.
        freeform_n_steps: int
            Registration starts with further downsampled versions of the
            original data to optimize the global fit of the result and prevent
            "getting stuck" in local minima of the similarity function. This
             parameter determines how many downsampling steps are being
             performed, with each step halving the data size along each
             dimension.
        freeform_use_n_steps: int
            Determines how many of the downsampling steps defined by
            freeform_n_steps will have their registration computed. The
            combination freeform_n_steps=3, freeform_use_n_steps=2 will e.g.
            calculate 3 downsampled steps, each of which is half the size of
             the previous one but only perform the registration on the 2
             smallest resampling steps, skipping the full resolution data.
             Can be used to save time if running the full resolution doesn't
             result in noticeable improvements
        bending_energy_weight: float
            Sets the bending energy, which is the coefficient of the penalty
             term, preventing the freeform registration from over-fitting.
             The range is between 0 and 1 (exclusive) with higher values
             leading to more restriction of the registration.
        grid_spacing: int
            Sets the control point grid spacing in x, y & z.
            Smaller grid spacing allows for more local deformations
             but increases the risk of over-fitting.
        smoothing_sigma_reference: int
            Adds a Gaussian smoothing to the reference image (the one being
            registered), with the sigma defined by the number. Positive
            values are interpreted as real values in mm, negative values
            are interpreted as distance in voxels.
        smoothing_sigma_floating: float
            Adds a Gaussian smoothing to the floating image (the one being
            registered), with the sigma defined by the number. Positive
            values are interpreted as real values in mm, negative values
            are interpreted as distance in voxels.
        histogram_n_bins_floating: float
            Number of bins used for the generation of the histograms used
            for the calculation of Normalized Mutual Information on the
            floating image
        histogram_n_bins_reference: float
             Number of bins used for the generation of the histograms used
             for the calculation of Normalized Mutual Information on the
             reference image
        debug: bool
            Activate debug mode (save intermediate steps).
        check_orientation_button:
            Interactively check the input orientation by comparing the average
            projection along each axis.  The top row of displayed images are
            the projections of the reference atlas. The bottom row are the
            projections of the aligned input data. If the two rows are
            similarly oriented, the orientation is correct. If not, change
            the orientation and try again.
        reset_button:
            Reset parameters to default
        block : bool
            If `True`, registration will block execution when called. By
            default this is `False` to avoid blocking the napari GUI, but
            is set to `True` in the tests.
        """

        def load_registration_as_layers() -> None:
            """
            Load the saved registration data into napari layers.
            """
            viewer = getattr(widget, "viewer").value
            registration_directory = pathlib.Path(
                getattr(widget, "registration_output_folder").value
            )
            add_registered_image_layers(
                viewer, registration_directory=registration_directory
            )

        def get_gui_logging_args():
            args_dict = {}
            args_dict.setdefault("image_paths", img_layer.source.path)
            args_dict.setdefault("backend", "niftyreg")

            voxel_sizes = []

            for name in ["z_pixel_um", "y_pixel_um", "x_pixel_um"]:
                voxel_sizes.append(str(getattr(widget, name).value))
            args_dict.setdefault("voxel_sizes", voxel_sizes)

            for name, value in DEFAULT_PARAMETERS.items():
                if "pixel" not in name:
                    if name == "atlas_key":
                        args_dict.setdefault(
                            "atlas", str(getattr(widget, name).value.value)
                        )

                    if name == "data_orientation":
                        args_dict.setdefault(
                            "orientation", str(getattr(widget, name).value)
                        )

                    args_dict.setdefault(
                        name, str(getattr(widget, name).value)
                    )

            return (
                namedtuple("namespace", args_dict.keys())(*args_dict.values()),
                args_dict,
            )

        @thread_worker
        def run():
            paths = Paths(pathlib.Path(registration_output_folder))

            niftyreg_args = NiftyregArgs(
                affine_n_steps,
                affine_use_n_steps,
                freeform_n_steps,
                freeform_use_n_steps,
                bending_energy_weight,
                -grid_spacing,
                -smoothing_sigma_reference,
                -smoothing_sigma_floating,
                histogram_n_bins_floating,
                histogram_n_bins_reference,
                debug=False,
            )
            args_namedtuple, args_dict = get_gui_logging_args()
            log_metadata(paths.metadata_path, args_dict)

            fancylog.start_logging(
                str(paths.registration_output_folder),
                program_for_log,
                variables=args_namedtuple,
                verbose=niftyreg_args.debug,
                log_header="BRAINREG LOG",
                multiprocessing_aware=False,
            )

            voxel_sizes = z_pixel_um, x_pixel_um, y_pixel_um

            (
                n_free_cpus,
                n_processes,
                atlas,
                scaling,
                load_parallel,
            ) = initialise_brainreg(
                atlas_key.value, data_orientation, voxel_sizes
            )

            additional_images_downsample = get_additional_images_downsample(
                widget
            )

            logging.info(f"Registering {img_layer._name}")

            target_brain = downsample_and_save_brain(img_layer, scaling)
            target_brain = bg.map_stack_to(
                data_orientation, atlas.metadata["orientation"], target_brain
            )
            sort_input_file = False
            run_niftyreg(
                registration_output_folder,
                paths,
                atlas,
                target_brain,
                n_processes,
                additional_images_downsample,
                data_orientation,
                atlas.metadata["orientation"],
                niftyreg_args,
                PRE_PROCESSING_ARGS,
                scaling,
                load_parallel,
                sort_input_file,
                n_free_cpus,
                save_original_orientation=save_original_orientation,
                brain_geometry=brain_geometry.value,
            )

            logging.info("Calculating volumes of each brain area")
            calculate_volumes(
                atlas,
                paths.registered_atlas,
                paths.registered_hemispheres,
                paths.volume_csv_path,
                # for all brainglobe atlases
                left_hemisphere_value=1,
                right_hemisphere_value=2,
            )

            logging.info("Generating boundary image")
            boundaries(paths.registered_atlas, paths.boundaries_file_path)

            logging.info(
                f"brainreg completed. Results can be found here: "
                f"{paths.registration_output_folder}"
            )

        worker = run()
        if not block:
            worker.returned.connect(load_registration_as_layers)

        worker.start()

        if block:
            worker.await_workers()
            load_registration_as_layers()

    @widget.reset_button.changed.connect
    def restore_defaults(event=None):
        for name, value in DEFAULT_PARAMETERS.items():
            if name not in ["atlas_key", "brain_geometry"]:
                getattr(widget, name).value = value

    @widget.check_orientation_button.changed.connect
    def check_orientation(event=None):
        """
        Function used to check that the input orientation is correct.
        To do so it transforms the input data into the requested atlas
        orientation, compute the average projection and displays it alongside
        the atlas. It is then easier for the user to identify which dimension
        should be swapped and avoid running the pipeline on wrongly aligned
        data.
        """

        if getattr(widget, "img_layer").value is None:
            show_info("Raw data must be loaded before checking orientation.")
            return widget

        # Get viewer object
        viewer = getattr(widget, "viewer").value

        brain_geometry = getattr(widget, "brain_geometry").value

        # Remove previous average projection layer if needed
        ind_pop = []
        for i, layer in enumerate(viewer.layers):
            if layer.name in [
                "Ref. proj. 0",
                "Ref. proj. 1",
                "Ref. proj. 2",
                "Input proj. 0",
                "Input proj. 1",
                "Input proj. 2",
            ]:
                ind_pop.append(i)
            else:
                layer.visible = False
        for index in ind_pop[::-1]:
            del viewer.layers[index]

        # Load atlas and gather data
        atlas = BrainGlobeAtlas(widget.atlas_key.value.name)
        if brain_geometry.value == "hemisphere_l":
            atlas.reference[
                atlas.hemispheres == atlas.left_hemisphere_value
            ] = 0
        elif brain_geometry.value == "hemisphere_r":
            atlas.reference[
                atlas.hemispheres == atlas.right_hemisphere_value
            ] = 0
        input_orientation = getattr(widget, "data_orientation").value
        data = getattr(widget, "img_layer").value.data
        # Transform data to atlas orientation from user input
        data_remapped = bg.map_stack_to(
            input_orientation, atlas.orientation, data
        )

        # Compute average projection of atlas and remapped data
        u_proj = []
        u_proja = []
        s = []
        for i in range(3):
            u_proj.append(np.mean(data_remapped, axis=i))
            u_proja.append(np.mean(atlas.reference, axis=i))
            s.append(u_proja[-1].shape[0])
        s = np.max(s)

        # Display all projections with somewhat consistent scaling
        viewer.add_image(u_proja[0], name="Ref. proj. 0")
        viewer.add_image(
            u_proja[1], translate=[0, u_proja[0].shape[1]], name="Ref. proj. 1"
        )
        viewer.add_image(
            u_proja[2],
            translate=[0, u_proja[0].shape[1] + u_proja[1].shape[1]],
            name="Ref. proj. 2",
        )

        s1 = u_proja[0].shape[0] / u_proj[0].shape[0]
        s2 = u_proja[0].shape[1] / u_proj[0].shape[1]
        viewer.add_image(
            u_proj[0], translate=[s, 0], name="Input proj. 0", scale=[s1, s2]
        )
        s1 = u_proja[1].shape[0] / u_proj[1].shape[0]
        s2 = u_proja[1].shape[1] / u_proj[1].shape[1]
        viewer.add_image(
            u_proj[1],
            translate=[s, u_proja[0].shape[1]],
            name="Input proj. 1",
            scale=[s1, s2],
        )
        s1 = u_proja[2].shape[0] / u_proj[2].shape[0]
        s2 = u_proja[2].shape[1] / u_proj[2].shape[1]
        viewer.add_image(
            u_proj[2],
            translate=[s, u_proja[0].shape[1] + u_proja[1].shape[1]],
            name="Input proj. 2",
            scale=[s1, s2],
        )

    return widget
