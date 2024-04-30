import logging
import tempfile
from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser
from datetime import datetime
from pathlib import Path

from brainglobe_utils.general.numerical import check_positive_int
from brainglobe_utils.general.system import ensure_directory_exists
from fancylog import fancylog

import brainreg as program_for_log
from brainreg import __version__
from brainreg.core.backend.niftyreg.parser import niftyreg_parse
from brainreg.core.main import main as register
from brainreg.core.paths import Paths
from brainreg.core.utils.misc import get_arg_groups, log_metadata

temp_dir = tempfile.TemporaryDirectory()
temp_dir_path = temp_dir.name


def register_cli_parser():
    parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)
    parser = cli_parse(parser)
    parser = atlas_parse(parser)
    parser = backend_parse(parser)
    parser = niftyreg_parse(parser)
    parser = pixel_parser(parser)
    parser = geometry_parser(parser)
    parser = misc_parse(parser)
    parser = preprocessing_parser(parser)

    return parser


def cli_parse(parser):
    cli_parser = parser.add_argument_group("brainreg registration options")

    cli_parser.add_argument(
        dest="image_paths",
        type=str,
        help="Path to the directory of the image files. Can also be a text"
        "file pointing to the files.",
    )

    cli_parser.add_argument(
        dest="brainreg_directory",
        type=str,
        help="Directory to save the output",
    )

    cli_parser.add_argument(
        "-a",
        "--additional",
        dest="additional_images",
        type=str,
        nargs="+",
        help="Paths to N additional channels to downsample to the same "
        "coordinate space. ",
    )
    cli_parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s {version}".format(version=__version__),
    )

    return parser


def atlas_parse(parser):
    atlas_parser = parser.add_argument_group("brainreg registration options")
    atlas_parser.add_argument(
        "--atlas",
        dest="atlas",
        type=str,
        default="allen_mouse_25um",
        help="Brainglobe atlas to use for registration. Run 'brainglobe list' "
        "to see the atlases available.",
    )
    return parser


def backend_parse(parser):
    atlas_parser = parser.add_argument_group("registration backend options")
    atlas_parser.add_argument(
        "--backend",
        dest="backend",
        type=str,
        default="niftyreg",
        help="Registration backend to use.",
    )
    return parser


def misc_parse(parser):
    misc_parser = parser.add_argument_group("Misc options")
    misc_parser.add_argument(
        "--n-free-cpus",
        dest="n_free_cpus",
        type=check_positive_int,
        default=2,
        help="The number of CPU cores on the machine to leave "
        "unused by the program to spare resources.",
    )

    misc_parser.add_argument(
        "--debug",
        dest="debug",
        action="store_true",
        help="Debug mode. Will increase verbosity of logging and save all "
        "intermediate files for diagnosis of software issues.",
    )

    misc_parser.add_argument(
        "--save-original-orientation",
        dest="save_original_orientation",
        action="store_true",
        help="Option to save the atlas annotations in the same orientation "
        "as the original data.",
    )

    misc_parser.add_argument(
        "--brain_geometry",
        default="full",
        dest="brain_geometry",
        help="Option to specify when the brain is not complete and which "
        "part it is."
        " Currently brainreg supports full ('full') brain, "
        "and half hemispheres "
        "('hemisphere_l'/'hemisphere_r').",
        choices=["full", "hemisphere_l", "hemisphere_r"],
    )

    misc_parser.add_argument(
        "--sort-input-file",
        dest="sort_input_file",
        action="store_true",
        help="If set to true, the input text file will be sorted using "
        "natural sorting. This means that the file paths will be "
        "sorted as would be expected by a human and "
        "not purely alphabetically",
    )
    return parser


def pixel_parser(parser):
    pixel_opt_parser = parser.add_argument_group(
        "Options to define pixel sizes of raw data"
    )
    pixel_opt_parser.add_argument(
        "-v",
        "--voxel-sizes",
        dest="voxel_sizes",
        required=True,
        nargs="+",
        # type=tuple,
        help="Voxel sizes in microns, in the order of data orientation. "
        "e.g. '5 2 2'",
    )

    return parser


def geometry_parser(parser):
    geometry_opt_parser = parser.add_argument_group(
        "Options to define size/shape/orientation of data"
    )

    geometry_opt_parser.add_argument(
        "--orientation",
        type=str,
        required=True,
        help="The orientation of the sample brain. "
        "This is used to transpose the atlas "
        "into the same orientation as the brain.",
    )

    return parser


def preprocessing_parser(parser):
    preprocessing_opt_parser = parser.add_argument_group(
        "Pre-processing options"
    )

    preprocessing_opt_parser.add_argument(
        "--pre-processing",
        dest="preprocessing",
        type=str,
        default="default",
        required=False,
        help="Pre-processing method to be applied before registration. "
        "Possible values: skip, default.",
    )

    return parser


def prep_registration(args):
    """
    Prepares the file system for registration.

    Ensures the brainreg directory exists and
    stores paths for additional channels
    that should be registered (if any were passed)
    into a dictionary.

    Dictionary keys for additional channel paths are
    - the file/folder name passed (if unique for all additional channels)
    - the file/folder name prefixed with the parent folder name (otherwise)

    Throws an error if multiple additional channels have
    the same name and the same parent folder, because the dictionary
    key is not unique in this situation.

    Parameters
    ----------
    args : argparse.Namespace
        ArgParse object. Expected attributes here are "brainreg_directory"
        and (optionally) "additional_images".

    Returns
    -------
    tuple
        A tuple containing the `args` object
        and the `additional_images_to_downsample` dictionary.

    """
    logging.debug("Making registration directory")
    ensure_directory_exists(args.brainreg_directory)

    additional_images_to_downsample = {}

    if args.additional_images:
        path_names = [
            Path(path).name for path in args.additional_images
        ]  # could be files or folders containing e.g. lots of 2D tiffs
        has_duplicate_names = any(
            path_names.count(name) > 1 for name in path_names
        )
        for additional_channel_paths in args.additional_images:
            channel_name = Path(additional_channel_paths).name
            if not has_duplicate_names:
                additional_images_to_downsample[channel_name] = (
                    additional_channel_paths
                )
            else:
                channel_name = Path(additional_channel_paths).name
                parent_folder = Path(additional_channel_paths).parent.name
                channel_name = f"{parent_folder}_{channel_name}"
                additional_images_to_downsample[channel_name] = (
                    additional_channel_paths
                )

        assert len(args.additional_images) == len(
            additional_images_to_downsample
        ), (
            "Something went wrong parsing additional channel names - "
            + "please ensure additional channels have a unique "
            + "combination of name and parent folder."
        )

    return args, additional_images_to_downsample


def main():
    start_time = datetime.now()
    args = register_cli_parser().parse_args()
    arg_groups = get_arg_groups(args, register_cli_parser())

    args, additional_images_downsample = prep_registration(args)

    paths = Paths(args.brainreg_directory)

    log_metadata(paths.metadata_path, args)

    fancylog.start_logging(
        paths.registration_output_folder,
        program_for_log,
        variables=[args],
        verbose=args.debug,
        log_header="BRAINREG LOG",
        multiprocessing_aware=False,
    )

    logging.info("Starting registration")

    register(
        args.atlas,
        args.orientation,
        args.image_paths,
        paths,
        args.voxel_sizes,
        arg_groups["NiftyReg registration backend options"],
        arg_groups["Pre-processing options"],
        sort_input_file=args.sort_input_file,
        n_free_cpus=args.n_free_cpus,
        additional_images_downsample=additional_images_downsample,
        backend=args.backend,
        debug=args.debug,
        save_original_orientation=args.save_original_orientation,
        brain_geometry=args.brain_geometry,
    )

    logging.info("Finished. Total time taken: %s", datetime.now() - start_time)


if __name__ == "__main__":
    main()
