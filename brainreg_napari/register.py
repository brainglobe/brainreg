import json
import napari
import pathlib
import logging

import bg_space as bg

from collections import namedtuple
from enum import Enum
from fancylog import fancylog
from magicgui import magicgui

from brainglobe_napari_io.cellfinder.reader_dir import load_registration
from brainreg_segment.atlas.utils import get_available_atlases

import brainreg as program_for_log
from brainreg.utils.misc import log_metadata
from brainreg.paths import Paths
from brainreg.utils.boundaries import boundaries
from brainreg.utils.volume import calculate_volumes
from brainreg.backend.niftyreg.run import run_niftyreg


def get_layer_labels(widget):
    return [layer._name for layer in widget.viewer.value.layers]


def get_additional_images_downsample(widget):
    names = [layer._name for layer in widget.viewer.value.layers.selection]
    filenames = [
        layer._source for layer in widget.viewer.value.layers.selection
    ]
    return {str(k): str(v.path) for k, v in zip(names, filenames)}


def get_atlas_dropdown():
    atlas_dict = {}
    for i, k in enumerate(get_available_atlases().keys()):
        atlas_dict.setdefault(k, k)
    atlas_keys = Enum("atlas_key", atlas_dict)
    return atlas_keys


def brainreg_register():
    from napari._qt.qthreading import thread_worker
    from brainreg_napari.util import (
        initialise_brainreg,
        downsample_and_save_brain,
        NiftyregArgs,
    )

    DEFAULT_PARAMETERS = dict(
        z_pixel_um=5,
        y_pixel_um=2,
        x_pixel_um=2,
        data_orientation="psl",
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
    )

    @magicgui(
        call_button=True,
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
            label="data_orientation",
        ),
        registration_output_folder=dict(
            value=DEFAULT_PARAMETERS["registration_output_folder"],
            mode="d",
            label="registration_output_folder",
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
        reset_button=dict(widget_type="PushButton", text="Reset defaults"),
    )
    def widget(
        viewer: napari.Viewer,
        img_layer: napari.layers.Image,
        atlas_key: get_atlas_dropdown(),
        data_orientation: str,
        z_pixel_um: float,
        x_pixel_um: float,
        y_pixel_um: float,
        registration_output_folder: pathlib.Path,
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
        reset_button,
    ):
        """

        :param img_layer:
        :param data_orientation:
        :param atlas_key:
        :param z_pixel_um:
        :param x_pixel_um:
        :param y_pixel_um:
        :param registration_output_folder:
        :param affine_n_steps:
        :param affine_use_n_steps:
        :param freeform_n_steps:
        :param freeform_use_n_steps:
        :param bending_energy_weight:
        :param grid_spacing:
        :param smoothing_sigma_reference:
        :param smoothing_sigma_floating:
        :param histogram_n_bins_floating:
        :param histogram_n_bins_reference:
        :return:
        """

        def add_image_layers():
            registration_directory = pathlib.Path(
                getattr(widget, "registration_output_folder").value
            )
            layers = []

            if registration_directory.exists():
                with open(
                    registration_directory / "brainreg.json"
                ) as json_file:
                    metadata = json.load(json_file)
                layers = load_registration(
                    layers, registration_directory, metadata
                )
            viewer = getattr(widget, "viewer").value
            atlas_layer = napari.layers.Labels(
                layers[0][0],
                scale=layers[0][1]["scale"],
                name=layers[0][1]["name"],
            )
            boundaries_layer = napari.layers.Image(
                layers[1][0],
                scale=layers[1][1]["scale"],
                name=layers[1][1]["name"],
            )
            viewer.add_layer(atlas_layer)
            viewer.add_layer(boundaries_layer)

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
        def run(
            affine_n_steps,
            affine_use_n_steps,
            freeform_n_steps,
            freeform_use_n_steps,
            bending_energy_weight,
            grid_spacing,
            smoothing_sigma_reference,
            smoothing_sigma_floating,
            histogram_n_bins_floating,
            histogram_n_bins_reference,
        ):

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
                scaling,
                load_parallel,
                sort_input_file,
                n_free_cpus,
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

        worker = run(
            affine_n_steps,
            affine_use_n_steps,
            freeform_n_steps,
            freeform_use_n_steps,
            bending_energy_weight,
            grid_spacing,
            smoothing_sigma_reference,
            smoothing_sigma_floating,
            histogram_n_bins_floating,
            histogram_n_bins_reference,
        )
        worker.returned.connect(add_image_layers)
        worker.start()

    @widget.reset_button.changed.connect
    def restore_defaults(event=None):
        for name, value in DEFAULT_PARAMETERS.items():
            if name != "atlas_key":
                getattr(widget, name).value = value

    return widget
