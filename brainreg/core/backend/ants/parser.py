
def ants_parse(parser):
    ants_opt_parser = parser.add_argument_group(
        "ANTs registration backend options"
    )
    ants_opt_parser.add_argument(
        "--ants-transform-type",
        dest="ants_transform_type",
        type=str,
        default="SyN",
        help="The type of transform to use for ANTs registration.",
        choices=["Affine", "Rigid", "SyN", "SyNQuick"],
    )
    return parser
