import json
from argparse import Namespace
from pathlib import PurePath

import pandas as pd


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


def safe_pandas_concat(df1: pd.DataFrame, df2: pd.DataFrame) -> pd.DataFrame:
    """
    Concatenate two DataFrames without relying on deprecated functionality
    when one of the DataFrames is empty.

    If df1 and df2 are non-empty, return the concatenation.
    If df1 is empty and df2 is not, return a copy of df2.
    If df1 is non-empty and df2 is, return a copy of df1.
    If df1 and df2 are empty, return an empty DataFrame with the same column names as df1.

    :param df1: DataFrame to concatenate.
    :param df2: DataFrame to concatenate.
    :returns: DataFrame formed from concatenation of df1 and df2.
    """
    if df1.empty and df2.empty:
        return pd.DataFrame(columns=df1.columns)
    elif df1.empty:
        return df2.copy()
    elif df2.empty:
        return df1.copy()
    else:
        return pd.concat([df1, df2], ignore_index=True)
