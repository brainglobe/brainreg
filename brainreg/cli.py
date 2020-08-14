import logging
import tempfile
from argparse import (
    ArgumentParser,
    ArgumentDefaultsHelpFormatter,
)
from datetime import datetime
from fancylog import fancylog
from pathlib import Path

from micrometa.micrometa import SUPPORTED_METADATA_TYPES
from imlib.general.system import ensure_directory_exists
from imlib.general.numerical import check_positive_int, check_positive_float
from imlib.image.metadata import define_pixel_sizes

from brainreg.utils.misc import get_arg_groups
from brainreg.main import main as register
from brainreg.backend.niftyreg.parser import niftyreg_parse
import brainreg as program_for_log

from bg_atlasapi.bg_atlas import BrainGlobeAtlas

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
        "-d",
        "--downsample",
        dest="downsample_images",
        type=str,
        nargs="+",
        help="Paths to N additional channels to downsample to the same "
        "coordinate space. ",
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
        default=4,
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
        "--metadata",
        dest="metadata",
        type=Path,
        help="Path to the metadata file. Supported formats are '{}'.".format(
            SUPPORTED_METADATA_TYPES
        ),
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
        "-x",
        "--x-pixel-um",
        dest="x_pixel_um",
        type=check_positive_float,
        help="Pixel spacing of the data in the first "
        "dimension, specified in um.",
    )
    pixel_opt_parser.add_argument(
        "-y",
        "--y-pixel-um",
        dest="y_pixel_um",
        type=check_positive_float,
        help="Pixel spacing of the data in the second "
        "dimension, specified in um.",
    )
    pixel_opt_parser.add_argument(
        "-z",
        "--z-pixel-um",
        dest="z_pixel_um",
        type=check_positive_float,
        help="Pixel spacing of the data in the third "
        "dimension, specified in um.",
    )
    return parser


def geometry_parser(parser):
    geometry_opt_parser = parser.add_argument_group(
        "Options to define size/shape/orientation of data"
    )

    geometry_opt_parser.add_argument(
        "--orientation",
        type=str,
        default="psl",
        help="The orientation of the sample brain. "
        "This is used to transpose the atlas "
        "into the same orientation as the brain.",
    )

    return parser


def prep_registration(args):
    logging.debug("Making registration directory")
    ensure_directory_exists(args.brainreg_directory)

    additional_images_downsample = {}
    if args.downsample_images:
        for idx, images in enumerate(args.downsample_images):
            name = Path(images).name
            additional_images_downsample[name] = images

    return args, additional_images_downsample


def main():
    start_time = datetime.now()
    args = register_cli_parser().parse_args()
    arg_groups = get_arg_groups(args, register_cli_parser())
    args = define_pixel_sizes(args)

    args, additional_images_downsample = prep_registration(args)

    fancylog.start_logging(
        args.brainreg_directory,
        program_for_log,
        variables=[args],
        verbose=args.debug,
        log_header="BRAINREG LOG",
        multiprocessing_aware=False,
    )

    logging.info("Starting registration")

    atlas = BrainGlobeAtlas(args.atlas)

    register(
        atlas,
        args.orientation,
        args.image_paths,
        args.brainreg_directory,
        arg_groups["NiftyReg registration backend options"],
        x_pixel_um=args.x_pixel_um,
        y_pixel_um=args.y_pixel_um,
        z_pixel_um=args.z_pixel_um,
        sort_input_file=args.sort_input_file,
        n_free_cpus=args.n_free_cpus,
        additional_images_downsample=additional_images_downsample,
        backend=args.backend,
        debug=args.debug,
    )

    logging.info("Finished. Total time taken: %s", datetime.now() - start_time)


if __name__ == "__main__":
    main()
