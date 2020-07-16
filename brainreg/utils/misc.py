from argparse import Namespace


def get_arg_groups(args, parser):
    arg_groups = {}
    for group in parser._action_groups:
        group_dict = {
            a.dest: getattr(args, a.dest, None) for a in group._group_actions
        }
        arg_groups[group.title] = Namespace(**group_dict)

    return arg_groups
