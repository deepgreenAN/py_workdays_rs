import numpy as np
import numpy.typing as npt
import pandas as pd
from typing import Any

from .py_workdays import extract_workdays_bool_naive, extract_intraday_bool_naive, extract_workdays_intraday_bool_naive


def extract_workdays_bool(dt_index: Any) -> npt.NDArray[np.bool_]:
    """
    pd.DatetimeIndexから，営業日のデータのものを抽出

    Parameters
    ----------
    dt_index: pd.DatetimeIndex
        入力するDatetimeIndex，すでにdatetimeでソートしていることが前提

    Returns
    -------
    営業日を抜き出したブールのndarray

    """        
    tz_dt = dt_index.tz
        
    if tz_dt is not None:
        naive_dt_index = dt_index.copy()
        naive_dt_index = naive_dt_index.tz_localize(None)  # 同じdatetimeの値をもつutc(python の localと挙動がことなることに注意)
    else:
        naive_dt_index = dt_index
        
    dt_value_datetime_64 = (naive_dt_index.values.astype(np.int64)/1.e9).astype(np.int64)
    extracted_bool = extract_workdays_bool_naive(dt_value_datetime_64)
    
    return extracted_bool


def extract_intraday_bool(dt_index: Any) -> npt.NDArray[np.bool_]:
    """
    pd.DatetimeIndexから，営業時間中のデータのものを抽出

    Parameters
    ----------
    dt_index: pd.DatetimeIndex
        入力するDatetimeIndex

    Returns
    -------
    営業時間を抜き出したブールのndarray
    """

    tz_dt = dt_index.tz
        
    if tz_dt is not None:
        naive_dt_index = dt_index.copy()
        naive_dt_index = naive_dt_index.tz_localize(None)  # 同じdatetimeの値をもつutc(python の localと挙動がことなることに注意)
    else:
        naive_dt_index = dt_index
        
    dt_value_datetime_64 = (naive_dt_index.values.astype(np.int64)/1.e9).astype(np.int64)
    extracted_bool = extract_intraday_bool_naive(dt_value_datetime_64)

    return extracted_bool


def extract_workdays_intraday_bool(dt_index: Any) -> npt.NDArray[np.bool_]:
    """
    pd.DatetimeIndexから，営業日+日中のデータのものを抽出．

    Parameters
    ----------
    dt_index: pd.DatetimeIndex
        入力するDatetimeIndex

    Returns
    -------
    営業日・営業時間を抜き出したブールのndarray

    Examples
    --------
    >>> datetime_list = [
        datetime.datetime(2021,1,1,0,0,0),
        datetime.datetime(2021,1,1,10,0,0),
        datetime.datetime(2021,1,4,0,0,0),
        datetime.datetime(2021,1,4,10,0,0)
        ]
    >>> datetime_index = pd.DatetimeIndex(datetime_list)
    >>> extract_workdays_intraday_bool(datetime_index)
    array([False, False, False,  True])
    """ 
    tz_dt = dt_index.tz
        
    if tz_dt is not None:
        naive_dt_index = dt_index.copy()
        naive_dt_index = naive_dt_index.tz_localize(None)  # 同じdatetimeの値をもつutc(python の localと挙動がことなることに注意)
    else:
        naive_dt_index = dt_index
        
    dt_value_datetime_64 = (naive_dt_index.values.astype(np.int64)/1.e9).astype(np.int64)
    extracted_bool = extract_workdays_intraday_bool_naive(dt_value_datetime_64)
    
    return extracted_bool

    
if __name__ == "__main__":
    pass