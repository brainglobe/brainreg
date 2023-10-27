import pandas as pd

from brainreg.core.utils.misc import safe_pandas_concat


def test_safe_pandas_concat() -> None:
    """
    Test the following:
    - Non-empty dataframes are concatenated as expected,
    - When one dataframe is empty, the other is returned,
    - When both dataframes are empty, an empty dataframe with
    the corresponding columns is returned.
    """
    df1 = pd.DataFrame(data={"a": [1], "b": [2], "c": [3]})
    df2 = pd.DataFrame(data={"a": [4], "b": [5], "c": [6]})
    empty_df = pd.DataFrame(columns=["a", "b", "c"])
    combined_df = pd.DataFrame(data={"a": [1, 4], "b": [2, 5], "c": [3, 6]})

    assert combined_df.equals(safe_pandas_concat(df1, df2))
    assert df1.equals(safe_pandas_concat(df1, empty_df))
    assert df2.equals(safe_pandas_concat(empty_df, df2))
    assert empty_df.equals(safe_pandas_concat(empty_df, empty_df))
    return
