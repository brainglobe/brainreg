import logging
import tempfile
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter, Namespace
from datetime import datetime
from fancylog import fancylog
from pathlib import Path

from micrometa.micrometa import SUPPORTED_METADATA_TYPES
from imlib.general.system import ensure_directory_exists
from imlib.general.numerical import check_positive_int, check_positive_float
from imlib.image.metadata import define_pixel_sizes


from brainreg.main import main as register

import brainreg as program_for_log

from bg_atlasapi.bg_atlas import AllenBrain25Um

temp_dir = tempfile.TemporaryDirectory()
temp_dir_path = temp_dir.name


def register_cli_parser():
    parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)
    parser = cli_parse(parser)
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
        dest="registration_output_folder",
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
    cli_parser.add_argument(
        "--sort-input-file",
        dest="sort_input_file",
        action="store_true",
        help="If set to true, the input text file will be sorted using "
        "natural sorting. This means that the file paths will be "
        "sorted as would be expected by a human and "
        "not purely alphabetically",
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
        default="asl",
        help="The orientation of the sample brain. "
        "This is used to transpose the atlas "
        "into the same orientation as the brain.",
    )

    return parser


def registration_parse(parser):
    registration_opt_parser = parser.add_argument_group("Registration options")
    registration_opt_parser.add_argument(
        "--sort-input-file",
        dest="sort_input_file",
        action="store_true",
        help="If set to true, the input text file will be sorted using "
        "natural sorting. This means that the file paths will be "
        "sorted as would be expected by a human and "
        "not purely alphabetically",
    )


def niftyreg_parse(parser):
    niftyreg_opt_parser = parser.add_argument_group(
        "NiftyReg registration backend options"
    )
    niftyreg_opt_parser.add_argument(
        "--affine-n-steps",
        dest="affine_n_steps",
        type=check_positive_int,
        default=6,
        help="Registration starts with further downsampled versions of the "
        "original data to optimize the global fit of the result and "
        "prevent 'getting stuck' in local minima of the similarity "
        "function. This parameter determines how many downsampling "
        "steps are being performed, with each step halving the data "
        "size along each dimension.",
    )
    niftyreg_opt_parser.add_argument(
        "--affine-use-n-steps",
        dest="affine_use_n_steps",
        type=check_positive_int,
        default=5,
        help=" Determines how many of the downsampling steps defined by "
        "-affine-n-steps will have their registration computed. "
        "The combination --affine-n-steps 3 --affine-use-n-steps 2 "
        "will e.g. calculate 3 downsampled steps, each of which is "
        "half the size of the previous one but only perform the "
        "registration on the 2 smallest resampling steps, skipping the "
        "full resolution data. Can be used to save time if running the "
        "full resolution doesn't result in noticeable improvements.",
    )
    niftyreg_opt_parser.add_argument(
        "--freeform-n-steps",
        dest="freeform_n_steps",
        type=check_positive_int,
        default=6,
        help=" Registration starts with further downsampled versions of the "
        "original data to optimize the global fit of the result and "
        "prevent 'getting stuck' in local minima of the similarity "
        "function. This parameter determines how many downsampling "
        "steps are being performed, with each step halving the data "
        "size along each dimension.",
    )
    niftyreg_opt_parser.add_argument(
        "--freeform-use-n-steps",
        dest="freeform_use_n_steps",
        type=check_positive_int,
        default=4,
        help="Determines how many of the downsampling steps defined by "
        "--freeform-n-steps will have their registration computed. "
        "The combination --freeform-n-steps 3 --freeform-use-n-steps "
        "2 will e.g. calculate 3 downsampled steps, each of which is "
        "half the size of the previous one but only perform the "
        "registration on the 2 smallest resampling steps, skipping the "
        "full resolution data. Can be used to save time if running the "
        "full resolution doesn't result in noticeable improvements.",
    )
    niftyreg_opt_parser.add_argument(
        "--bending-energy-weight",
        dest="bending_energy_weight",
        type=check_positive_float,
        default=0.95,
        help="Sets the bending energy, which is the coefficient of the "
        "penalty term, preventing the freeform registration from "
        "over-fitting. The range is between 0 and 1 (exclusive) "
        "with higher values leading to more restriction of the "
        "registration.",
    )
    niftyreg_opt_parser.add_argument(
        "--grid-spacing",
        dest="grid_spacing",
        type=int,
        default=-10,
        help="Sets the control point grid spacing in x, y & z. Positive "
        "values are interpreted as real values in mm, negative values "
        "are interpreted as the (positive) distances in voxels. Smaller "
        "grid spacing allows for more local deformations but increases "
        "the risk of over-fitting.",
    )
    niftyreg_opt_parser.add_argument(
        "--smoothing-sigma-reference",
        dest="smoothing_sigma_reference",
        type=float,
        default=-1.0,
        help="Adds a Gaussian smoothing to the reference (the one being "
        "registered to) image, with the sigma defined by the number. "
        "Positive values are interpreted as real values in mm, "
        "negative values are interpreted as distance in voxels.",
    )
    niftyreg_opt_parser.add_argument(
        "--smoothing-sigma-floating",
        dest="smoothing_sigma_floating",
        type=float,
        default=-1.0,
        help="Adds a Gaussian smoothing to the floating image (the one being "
        "registered), with the sigma defined by the number. Positive "
        "values are interpreted as real values in mm, negative values "
        "are interpreted as distance in voxels.",
    )
    niftyreg_opt_parser.add_argument(
        "--histogram-n-bins-floating",
        dest="histogram_n_bins_floating",
        type=check_positive_int,
        default=128,
        help="Number of bins used for the generation of the histograms used "
        "for the calculation of Normalized Mutual Information on "
        "the floating image.",
    )
    niftyreg_opt_parser.add_argument(
        "--histogram-n-bins-reference",
        dest="histogram_n_bins_reference",
        type=check_positive_int,
        default=128,
        help="Number of bins used for the generation of the histograms used "
        "for the calculation of Normalized Mutual Information on the "
        "reference image",
    )
    return parser


def prep_registration(args):
    logging.debug("Making registration directory")
    ensure_directory_exists(args.registration_output_folder)

    additional_images_downsample = {}
    if args.downsample_images:
        for idx, images in enumerate(args.downsample_images):
            name = Path(images).name
            additional_images_downsample[name] = images

    return args, additional_images_downsample


def get_arg_groups(args, parser):
    arg_groups = {}
    for group in parser._action_groups:
        group_dict = {
            a.dest: getattr(args, a.dest, None) for a in group._group_actions
        }
        arg_groups[group.title] = Namespace(**group_dict)

    return arg_groups


def run():
    start_time = datetime.now()
    args = register_cli_parser().parse_args()
    arg_groups = get_arg_groups(args, register_cli_parser())

    args = define_pixel_sizes(args)

    args, additional_images_downsample = prep_registration(args)

    fancylog.start_logging(
        args.registration_output_folder,
        program_for_log,
        variables=[args],
        verbose=args.debug,
        log_header="BRAINREG LOG",
        multiprocessing_aware=False,
    )

    logging.info("Starting registration")

    atlas = AllenBrain25Um()
    # TODO: get this from atlas metadata
    atlas_orientation = "asl"

    register(
        atlas,
        atlas_orientation,
        args.orientation,
        args.image_paths,
        args.registration_output_folder,
        arg_groups["NiftyReg registration backend options"],
        x_pixel_um=args.x_pixel_um,
        y_pixel_um=args.y_pixel_um,
        z_pixel_um=args.z_pixel_um,
        sort_input_file=args.sort_input_file,
        n_free_cpus=args.n_free_cpus,
        additional_images_downsample=additional_images_downsample,
        debug=args.debug,
    )

    logging.info("Finished. Total time taken: %s", datetime.now() - start_time)


def main():
    run()


if __name__ == "__main__":
    run()
