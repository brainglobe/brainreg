import json
from argparse import Namespace
from pathlib import PurePath


def get_arg_groups(args, parser):
    arg_groups = {}
    for group in parser._action_groups:
        group_dict = {
            a.dest: getattr(args, a.dest, None) for a in group._group_actions
        }
        arg_groups[group.title] = Namespace(**group_dict)

    return arg_groups


def serialise(obj):
    if isinstance(obj, PurePath):
        return str(obj)
    else:
        return obj.__dict__


def log_metadata(file_path, args):
    with open(file_path, "w") as f:
        json.dump(args, f, default=serialise)
