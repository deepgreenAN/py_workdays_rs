from datetime import timedelta, datetime
from pytz import timezone
from typing import List, Optional, Tuple, Any

from .py_workdays import *

def get_timezone_from_datetime(*arg_datetimes:datetime) -> Any:
    """
    awareなdatetimeのtimezoneを取得するnaiveの場合Noneが返る

    Parameters
    ----------
    arg_datetime: datetime
        timezoneを取得したいdatetime

    Returns
    -------
    any
        datetimeのtimezone
    """
    timezone_str_list: List[Optional[str]] = []
    for one_datetime in arg_datetimes:
        if one_datetime.tzinfo is not None:
            timezone_str_list.append(str(one_datetime.tzinfo))
        else:
            timezone_str_list.append(None)
            
    timezone_str_set = set(timezone_str_list)
    
    if len(timezone_str_set) > 1:
        raise Exception("arg_datetimes timezone must be same")
        
    if timezone_str_list[0] is not None:
        return timezone(timezone_str_list[0])
    else:
        return None


def check_workday_intraday(select_datetime: datetime) -> bool:
    """
    与えられたdatetime.datetimeが営業日・営業時間内であるかどうかを出力する

    Parameters
    ----------
    select_datetime: datetime.datetime
        入力するdatetime

    Returns
    -------
    bool
        営業日・営業時間内であるかどうか

    Examples
    --------
    >>> select_datetime = datetime.datetime(2021,1,4,10,0,0)
    >>> check_workday_intraday(select_datetime)
    True
    """
    assert isinstance(select_datetime, datetime)
    select_timezone = get_timezone_from_datetime(select_datetime)
    if select_timezone is not None:
        select_datetime = select_datetime.replace(tzinfo=None)
        
    return check_workday_intraday_naive(select_datetime)


def get_next_border_workday_intraday(select_datetime: datetime) -> Tuple[datetime, str]:
    """
    引数のdatetime.datetimeに最も近い後の営業時間を境界シンボルと共に返す

    Parameters
    ----------
    select_datetime: datetime.datetime
        指定する日時
        
    Returns
    -------
    out_datetime: datetime.datetime
        営業時間境界の日時
    boder_symbol: str
        out_datetimeが開始か終了かを示す文字列
            - "border_start": 営業時間の開始時刻
            - "border_end": 営業時間の終了時刻

    Examples
    --------
    >>> select_datetime = datetime.datetime(2021,1,1,0,0,0)
    >>> get_next_border_workday_intraday(select_datetime)
    (datetime.datetime(2021, 1, 4, 9, 0), 'border_start')
    """
    assert isinstance(select_datetime, datetime)
    select_timezone = get_timezone_from_datetime(select_datetime)
    if select_timezone is not None:
        select_datetime = select_datetime.replace(tzinfo=None)
     
    (next_datetime, next_symbol) = get_next_border_workday_intraday_naive(select_datetime)

    if select_timezone is not None:
        next_datetime = select_timezone.localize(next_datetime)
    
    return (next_datetime, next_symbol)


def get_previous_border_workday_intraday(select_datetime: datetime, force_is_end: bool=False) -> Tuple[datetime, str]:
    """
    引数のdatetime.datetimeに最も近い前の営業時間を境界シンボルと共に返す

    Parameters
    ----------
    select_datetime: datetime.datetime
        指定する日時
    force_is_end: bool
        終了境界だった場合にその営業時間の開始境界を求めるどうか
        
    Returns
    -------
    out_datetime: datetime.datetime
        営業時間境界の日時
    boder_symbol: str
        out_datetimeが開始か終了かを示す文字列
            - "border_start": 営業時間の開始時刻
            - "border_end": 営業時間の終了時刻
    """
    assert isinstance(select_datetime, datetime)
    select_timezone = get_timezone_from_datetime(select_datetime)
    if select_timezone is not None:
        select_datetime = select_datetime.replace(tzinfo=None)
        
    (previous_datetime, previous_symbol) = get_previous_border_workday_intraday_naive(
        select_datetime, 
        force_is_end
    )

    if select_timezone is not None:
        previous_datetime = select_timezone.localize(previous_datetime)
    
    return (previous_datetime, previous_symbol)


def get_near_workday_intraday(select_datetime: datetime, is_after: bool=True) -> Tuple[datetime, str]:
    """
    引数のdatetime.datetimeが営業日・営業時間の場合はそのまま，そうでない場合は最も近い境界を境界シンボルとともに返す．

    Parameters
    ----------
    select_datetime: datetime.datetime
        指定する日時
    is_after: bool
        後ろを探索するかどうか
        
    Returns
    -------
    out_datetime: datetime.datetime
        営業日・営業時間（あるいはボーダー）の日時
    boder_symbol: str
        out_datetimeがボーダーであるか・そうだとして開始か終了かを示す文字列
            - "border_intra": 営業時間内
            - "border_start": 営業時間の開始時刻
            - "border_end": 営業時間の終了時刻
    """
    assert isinstance(select_datetime, datetime)
    select_timezone = get_timezone_from_datetime(select_datetime)
    if select_timezone is not None:
        select_datetime = select_datetime.replace(tzinfo=None)
    
    (near_datetime, near_symbol) = get_near_workday_intraday_naive(
        select_datetime, 
        is_after
    )

    if select_timezone is not None:
        near_datetime = select_timezone.localize(near_datetime)
    
    return (near_datetime, near_symbol)


def add_workday_intraday_datetime(select_datetime: datetime, delta_time: timedelta) -> datetime:
    """
    営業日・営業時間を考慮しdatetime.datetimeを加算する．

    Parameters
    ----------
    select_datetime: datetime.datetime
        指定する日時
    delta_time: datetime.timedelta
        加算するtimedelta(ミリ秒は切り捨て)

    Returns
    -------
    added_datetime: datetime.datetime
        追加された日時

    Examples
    --------
    >>> select_datetime = datetime.datetime(2021,1,1,0,0,0)
    >>> add_workday_intraday_datetime(select_datetime, datetime.timedelta(hours=2))
    datetime.datetime(2021, 1, 4, 11, 0)
    """
    assert isinstance(select_datetime, datetime)
    
    select_timezone = get_timezone_from_datetime(select_datetime)
    if select_timezone is not None:
        select_datetime = select_datetime.replace(tzinfo=None)
    
    added_datetime = add_workday_intraday_datetime_naive(
        select_datetime, 
        delta_time
    )
    
    if select_timezone is not None:
        added_datetime = select_timezone.localize(added_datetime)  
        
    return added_datetime


def get_timedelta_workdays_intraday(start_datetime: datetime, end_datetime: datetime) -> timedelta:
    """
    指定期間中の営業日・営業時間をtimedelta(ミリ秒は切り捨て)として出力

    Parameters
    ----------
    start_datetime: datetime.datetime
        指定期間の開始日時
    end_datetime: datetime.datetime
        指定期間の終了日時

    Returns
    -------
    timedelta
        営業時間中のtimedelta

    Examples
    --------
    >>> start_datetime = datetime.datetime(2021,1,1,0,0,0)
    >>> end_datetime = datetime.datetime(2021,1,4,15,0,0)
    >>> get_timedelta_workdays_intraday(start_datetime, end_datetime)
    datetime.timedelta(seconds=18000)
    """
    assert isinstance(start_datetime, datetime)
    assert isinstance(end_datetime, datetime)
    
    select_timezone = get_timezone_from_datetime(start_datetime, end_datetime)
    if select_timezone is not None:
        start_datetime = start_datetime.replace(tzinfo=None)
        end_datetime = end_datetime.replace(tzinfo=None)
    
    delta_time = get_timedelta_workdays_intraday_naive(
        start_datetime, 
        end_datetime
    )
    
    return delta_time


if __name__ == "__main__":
    pass