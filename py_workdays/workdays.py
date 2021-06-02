import datetime
from typing import Optional
import numpy as np
import pandas as pd

#import sys
#sys.path.append("py_workdays/rs_workdays/target/release")

from rs_workdays import check_workday_rs 
from rs_workdays import get_next_workday_rs, get_previous_workday_rs, get_near_workday_rs
from rs_workdays import extract_workdays_bool_numpy_rs
#from .option import option


def get_workdays(start_date: datetime.date, end_date: datetime.date, closed: Optional[str]="left") -> np.ndarray:
    """
    営業日を取得
    
    Parameters
    ----------
    start_date: datetime.date
        開始時刻のdate
    end_datetime: datetime.date
        終了時刻のdate
    closed: Optional[str]
        境界を含めるかどうかを意味する文字列
            - 'left': 開始日を含める
            - 'right': 終了日を含める
            -  None: どちらも含める

    Returns
    -------
    date_array: np.ndarray[datetime.date]
        営業日のndarray

    Examples
    --------
    >>> start_date = datetime.date(2021,1,1)
    >>> end_date = datetime.date(2021,2,1)
    >>> get_workdays(start_date, end_date)
    array([datetime.date(2021, 1, 4), datetime.date(2021, 1, 5),
        datetime.date(2021, 1, 6), datetime.date(2021, 1, 7),
        datetime.date(2021, 1, 8), datetime.date(2021, 1, 12),
        datetime.date(2021, 1, 13), datetime.date(2021, 1, 14),
        datetime.date(2021, 1, 15), datetime.date(2021, 1, 18),
        datetime.date(2021, 1, 19), datetime.date(2021, 1, 20),
        datetime.date(2021, 1, 21), datetime.date(2021, 1, 22),
        datetime.date(2021, 1, 25), datetime.date(2021, 1, 26),
        datetime.date(2021, 1, 27), datetime.date(2021, 1, 28),
        datetime.date(2021, 1, 29)], dtype=object)
    """
    assert isinstance(start_date, datetime.date) and isinstance(end_date, datetime.date)
    assert not isinstance(start_date, datetime.datetime) and not isinstance(end_date, datetime.datetime)
    # closedについて
    closed_set = {"left", "right", None}
    if not closed in closed_set:
        raise Exception("closed must be any in {}".format(closed_set))
        
    all_date = pd.date_range(start_date, end_date, freq="D", closed=closed)
    all_date_datetime64 = (all_date.values.astype(np.int64) / 1.e9).astype(np.int64)
    date_array = all_date[extract_workdays_bool_numpy_rs(all_date_datetime64)].date.copy()
    
    return date_array


def get_not_workdays(start_date: datetime.date, end_date: datetime.date, closed: Optional[str]="left") -> np.ndarray:
    """
    非営業日を取得(休日曜日or祝日)

    Parameters
    ----------
    start_date: datetime.date
        開始時刻のdate
    end_datetime: datetime.date
        終了時刻のdate
    closed: Optional[str]
        境界を含めるかどうかを意味する文字列
            - 'left': 開始日を含める
            - 'right': 終了日を含める
            -  None: どちらも含める

    Returns
    -------
    date_array: np.ndarray[datetime.date]
        非営業日のndarray    
    """
    assert isinstance(start_date, datetime.date) and isinstance(end_date, datetime.date)
    assert not isinstance(start_date, datetime.datetime) and not isinstance(end_date, datetime.datetime)
    # closedについて
    closed_set = {"left", "right", None}
    if not closed in closed_set:
        raise Exception("closed must be any in {}".format(closed_set))
        
    all_date = pd.date_range(start_date, end_date, freq="D", closed=closed)
    all_date_datetime64 = (all_date.values.astype(np.int64) / 1.e9).astype(np.int64)
    date_array = all_date[~extract_workdays_bool_numpy_rs(all_date_datetime64)].date.copy()
    
    return date_array


def check_workday(select_date: datetime.date) -> bool:
    """
    与えられたdatetime.dateが営業日であるかどうかを出力する

    Parameters
    ----------
    select_date: datetime.date
        入力するdate

    Returns
    -------
    bool
        営業日であるかどうか

    Examples
    --------
    >>> select_date = datetime.date(2021,1,1)
    >>> check_workday(select_date)
    False
    """
    assert isinstance(select_date, datetime.date)
    assert not isinstance(select_date, datetime.datetime)
    select_date_str = select_date.strftime("%Y-%m-%d")

    return check_workday_rs(select_date_str)


def get_next_workday(select_date: datetime.date, days: int=1) -> datetime.date:
    """
    指定した日数後の営業日を取得

    Parameters
    ----------
    select_date: datetime.date
        指定する日時
    days: int
        日数

    Returns
    -------
    next_date: datetime.date
        次の営業日

    Examples
    --------
    >>> select_date = datetime.date(2021,1,1)
    >>> get_next_workday(select_date, days=6)
    datetime.date(2021, 1, 12)
    """
    assert isinstance(select_date, datetime.date)
    assert not isinstance(select_date, datetime.datetime)
    select_date_str = select_date.strftime("%Y-%m-%d")

    next_date_str = get_next_workday_rs(select_date_str, days)
    next_date = datetime.datetime.strptime(next_date_str, "%Y-%m-%d").date()
    
    return next_date


def get_previous_workday(select_date: datetime.date, days: int=1) -> datetime.date:
    """
    指定した日数前の営業日を取得

    Parameters
    ----------
    select_date: datetime.date
        指定する日時
    days: int
        日数

    Returns
    -------
    previous_date: datetime.date
        前の営業日
    """
    assert isinstance(select_date, datetime.date)
    assert not isinstance(select_date, datetime.datetime)
    select_date_str = select_date.strftime("%Y-%m-%d")
    
    previous_date_str = get_previous_workday_rs(select_date_str, days)
    previous_date = datetime.datetime.strptime(previous_date_str, "%Y-%m-%d").date()
    
    return previous_date


def get_near_workday(select_date: datetime.date, is_after: bool=True) -> datetime.date:
    """
    引数の最近の営業日を取得

    Parameters
    ----------
    select_date: datetime.date
        指定する日時
    is_aftaer: bool
        指定日時の後が前か

    Returns
    -------
    near_date: datetime.date
        最近の営業日
    """
    assert isinstance(select_date, datetime.date)
    assert not isinstance(select_date, datetime.datetime)
    
    select_date_str = select_date.strftime("%Y-%m-%d")
    
    near_date_str = get_near_workday_rs(select_date_str, is_after)
    near_date = datetime.datetime.strptime(near_date_str, "%Y-%m-%d").date()
    
    return near_date


def get_workdays_number(start_date: datetime.date, days: int) -> np.ndarray:
    """
    指定した日数分の営業日を取得

    Parameters
    ----------
    start_date: datetime.date
        開始日時
    days: int
        日数

    Returns
    -------
    datetime.date
        前か次の営業日

    Examples
    --------
    >>> start_date = datetime.date(2021,1,1)
    >>> days = 19
    >>> get_workdays_number(start_date, days)
    array([datetime.date(2021, 1, 4), datetime.date(2021, 1, 5),
        datetime.date(2021, 1, 6), datetime.date(2021, 1, 7),
        datetime.date(2021, 1, 8), datetime.date(2021, 1, 12),
        datetime.date(2021, 1, 13), datetime.date(2021, 1, 14),
        datetime.date(2021, 1, 15), datetime.date(2021, 1, 18),
        datetime.date(2021, 1, 19), datetime.date(2021, 1, 20),
        datetime.date(2021, 1, 21), datetime.date(2021, 1, 22),
        datetime.date(2021, 1, 25), datetime.date(2021, 1, 26),
        datetime.date(2021, 1, 27), datetime.date(2021, 1, 28),
        datetime.date(2021, 1, 29)], dtype=object)
    """
    assert isinstance(start_date, datetime.date)
    assert not isinstance(start_date, datetime.datetime)
    assert isinstance(days, int)
    
    if days > 0:
        start_date = start_date
        end_date = get_next_workday(start_date, days)
        if check_workday(start_date):  # start_dateを含める
            return get_workdays(start_date, end_date, closed="left")
        else:
            return get_workdays(start_date, end_date, closed=None)
    
    elif days < 0:
        end_date = start_date
        start_date = get_previous_workday(end_date, abs(days))
        if check_workday(end_date):  # end_dateを含める
            return get_workdays(end_date, start_date, closed="right")[::-1]
        else:
            return get_workdays(end_date, start_date, closed=None)[::-1]
    
    else :
        raise Exception("days must not be 0")


    if __name__ == "__main__":
        pass