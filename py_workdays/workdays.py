import datetime
import numpy as np
import pandas as pd

#import sys
#sys.path.append("py_workdays/rs_workdays/target/release")

from rs_workdays import check_workday_rs 
from rs_workdays import get_next_workday_rs, get_previous_workday_rs, get_near_workday_rs
from rs_workdays import extract_workdays_bool_numpy_rs
#from .option import option


def get_workdays(start_date, end_date, closed="left"):
    """
    営業日を取得
    
    start_date: datetime.date
        開始時刻のdate
    end_datetime: datetime.date
        終了時刻のdate
    closed: Option(str)
        境界を含めるかどうかを意味する文字列
        - 'left': 開始日を含める
        - 'right': 終了日を含める
        -  None: どちらも含める
    """
    assert isinstance(start_date, datetime.date) and isinstance(end_date, datetime.date)
    assert not isinstance(start_date, datetime.datetime) and not isinstance(end_date, datetime.datetime)
    # closedについて
    closed_set = {"left", "right", None}
    if not closed in closed_set:
        raise Exception("closed must be any in {}".format(closed_set))
        
    all_date = pd.date_range(start_date, end_date, freq="D", closed=closed)
    all_date_datetime64 = (all_date.values.astype(np.int64) / 1.e9).astype(np.int64)
    date_array = all_date.date[extract_workdays_bool_numpy_rs(all_date_datetime64)].copy()
    
    return date_array


def get_not_workdays(start_date, end_date, closed="left"):
    """
    非営業日を取得(休日曜日or祝日)
    
    start_date: datetime.date
        開始時刻のdate
    end_datetime: datetime.date
        終了時刻のdate
    closed: Option(str)
        境界を含めるかどうかを意味する文字列
        - 'left': 開始日を含める
        - 'right': 終了日を含める
        -  None: どちらも含めない
    """
    assert isinstance(start_date, datetime.date) and isinstance(end_date, datetime.date)
    assert not isinstance(start_date, datetime.datetime) and not isinstance(end_date, datetime.datetime)
    # closedについて
    closed_set = {"left", "right", None}
    if not closed in closed_set:
        raise Exception("closed must be any in {}".format(closed_set))
        
    all_date = pd.date_range(start_date, end_date, freq="D", closed=closed)
    all_date_datetime64 = (all_date.values.astype(np.int64) / 1.e9).astype(np.int64)
    date_array = all_date.date[~extract_workdays_bool_numpy_rs(all_date_datetime64)].copy()
    
    return date_array


def check_workday(select_date):
    """
    与えられたdatetime.dateが営業日であるかどうかを出力する
    select_date: datetime.date
        入力するdate
    """
    assert isinstance(select_date, datetime.date)
    assert not isinstance(select_date, datetime.datetime)
    select_date_str = select_date.strftime("%Y-%m-%d")

    return check_workday_rs(select_date_str)


def get_next_workday(select_date, days=1):
    """
    指定した日数後の営業日を取得
    select_date: datetime.date
        指定する日時
    days: int
        日数
    """
    assert isinstance(select_date, datetime.date)
    assert not isinstance(select_date, datetime.datetime)
    select_date_str = select_date.strftime("%Y-%m-%d")

    next_date_str = get_next_workday_rs(select_date_str, days)
    next_date = datetime.datetime.strptime(next_date_str, "%Y-%m-%d").date()
    
    return next_date


def get_previous_workday(select_date, days=1):
    """
    指定した日数前の営業日を取得
    select_date: datetime.date
        指定する日時
    days: int
        日数
    """
    assert isinstance(select_date, datetime.date)
    assert not isinstance(select_date, datetime.datetime)
    select_date_str = select_date.strftime("%Y-%m-%d")
    
    previous_date_str = get_previous_workday_rs(select_date_str, days)
    previous_date = datetime.datetime.strptime(previous_date_str, "%Y-%m-%d").date()
    
    return previous_date


def get_near_workday(select_date, is_after=True):
    """
    引数の最近の営業日を取得
    select_date: datetime.date
        指定する日時
    is_aftaer: bool
        指定日時の後が前か
    """
    assert isinstance(select_date, datetime.date)
    assert not isinstance(select_date, datetime.datetime)
    
    select_date_str = select_date.strftime("%Y-%m-%d")
    
    near_date_str = get_near_workday_rs(select_date_str, is_after)
    near_date = datetime.datetime.strptime(near_date_str, "%Y-%m-%d").date()
    
    return near_date


def get_workdays_number(start_date, days):
    """
    指定した日数分の営業日を取得
    start_date: datetime.date
        開始日時
    days: int
        日数
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