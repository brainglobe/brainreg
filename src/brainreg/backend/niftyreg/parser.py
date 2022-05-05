from imlib.general.numerical import check_positive_int, check_positive_float


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
