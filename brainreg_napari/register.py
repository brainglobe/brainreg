import napari
from magicgui import magicgui
import pathlib
from brainreg.paths import Paths
from brainreg.utils.boundaries import boundaries
from brainreg.utils.volume import calculate_volumes
import bg_space as bg
import logging
from brainreg.backend.niftyreg.run import run_niftyreg


def brainreg_register():
    from napari._qt.qthreading import thread_worker
    from brainreg_napari.util import (
        initialise_brainreg,
        downsample_and_save_brain,
        NiftyregArgs,
    )

    DEFAULT_PARAMETERS = dict(
        voxel_size_z=5,
        voxel_size_y=2,
        voxel_size_x=2,
        data_orientation="psl",
        atlas_key="allen_mouse_25um",
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
        voxel_size_z=dict(
            value=DEFAULT_PARAMETERS["voxel_size_z"],
            label="Voxel size (z)",
            step=0.1,
        ),
        voxel_size_y=dict(
            value=DEFAULT_PARAMETERS["voxel_size_y"],
            label="Voxel size (y)",
            step=0.1,
        ),
        voxel_size_x=dict(
            value=DEFAULT_PARAMETERS["voxel_size_x"],
            label="Voxel size (x)",
            step=0.1,
        ),
        data_orientation=dict(
            value=DEFAULT_PARAMETERS["data_orientation"],
            label="data_orientation",
        ),
        atlas_key=dict(
            value=DEFAULT_PARAMETERS["atlas_key"], label="atlas_key"
        ),
        registration_output_folder=dict(
            value=DEFAULT_PARAMETERS["registration_output_folder"], mode='d',
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
        # call_button=True,
    )
    def widget(
        img_layer: "napari.layers.Image",
        data_orientation: str,
        atlas_key: str,
        voxel_size_z: float,
        voxel_size_x: float,
        voxel_size_y: float,
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
        :param voxel_size_z:
        :param voxel_size_x:
        :param voxel_size_y:
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
            )

            voxel_sizes = voxel_size_z, voxel_size_x, voxel_size_y

            (
                n_free_cpus,
                n_processes,
                atlas,
                additional_images_downsample,
                scaling,
                load_parallel,
            ) = initialise_brainreg(atlas_key, data_orientation, voxel_sizes)
            target_brain = downsample_and_save_brain(img_layer, scaling)
            target_brain = bg.map_stack_to(
                data_orientation, atlas.metadata["orientation"], target_brain
            )

            paths = Paths(pathlib.Path(registration_output_folder))
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
        worker.start()

    @widget.reset_button.changed.connect
    def restore_defaults(event=None):
        for name, value in DEFAULT_PARAMETERS.items():
            getattr(widget, name).value = value

    return widget
