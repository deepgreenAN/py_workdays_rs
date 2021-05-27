import datetime
import numpy as np
import pandas as pd
import datetime
from datetime import timedelta
from pytz import timezone

import sys
#sys.path.append("py_workdays/rs_workdays/target/release")

from rs_workdays import check_workday_intraday_rs, get_next_border_workday_intraday_rs, get_previous_border_workday_intraday_rs
from rs_workdays import get_near_workday_intraday_rs
from rs_workdays import add_workday_intraday_datetime_rs, sub_workday_intraday_datetime_rs, get_timedelta_workdays_intraday_rs

#from .option import option  # 必須


def get_timezone_from_datetime(*arg_datetimes):
    """
    awareなdatetimeのtimezoneを取得するnaiveの場合Noneが返る
    arg_datetime: *datetime
        timezoneを取得したいdatetime
    """
    timezone_str_list = []
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


def check_workday_intraday(select_datetime):
    """
    与えられたdatetime.datetimeが営業日・営業時間内であるかどうかを出力する
    select_datetime: datetime.datetime
        入力するdatetime
    """
    assert isinstance(select_datetime, datetime.datetime)
    select_timezone = get_timezone_from_datetime(select_datetime)
    if select_timezone is not None:
        select_datetime = select_datetime.replace(tzinfo=None)
        
    select_datetime_str = datetime.datetime.strftime(select_datetime, "%Y-%m-%d %H:%M:%S")

    return check_workday_intraday_rs(select_datetime_str)


def get_next_border_workday_intraday(select_datetime):
    """
    引数のdatetime.datetimeに最も近い後の営業時間を境界シンボルと共に返す
    Paremeters
    ----------
    select_datetime: datetime.datetime
        指定する日時
        
    Returns
    -------
    out_datetime: datetime.datetime
        営業時間境界の日時
    boder_symbol: str
        out_datetimeが開始か終了かを示す文字列
            "border_start": 営業時間の開始時刻
            "border_end": 営業時間の終了時刻
    """
    assert isinstance(select_datetime, datetime.datetime)
    select_timezone = get_timezone_from_datetime(select_datetime)
    if select_timezone is not None:
        select_datetime = select_datetime.replace(tzinfo=None)
    
    select_datetime_str = datetime.datetime.strftime(select_datetime, "%Y-%m-%d %H:%M:%S")
    
    (next_datetime_str, next_symbol) = get_next_border_workday_intraday_rs(select_datetime_str)
    next_datetime = datetime.datetime.strptime(next_datetime_str, "%Y-%m-%d %H:%M:%S")
    if select_timezone is not None:
        next_datetime = select_timezone.localize(next_datetime)
    
    return (next_datetime, next_symbol)


def get_previous_border_workday_intraday(select_datetime, force_is_end=False):
    """
    引数のdatetime.datetimeに最も近い前の営業時間を境界シンボルと共に返す
    Paremeters
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
            "border_start": 営業時間の開始時刻
            "border_end": 営業時間の終了時刻
    """
    assert isinstance(select_datetime, datetime.datetime)
    select_timezone = get_timezone_from_datetime(select_datetime)
    if select_timezone is not None:
        select_datetime = select_datetime.replace(tzinfo=None)
    
    select_datetime_str = datetime.datetime.strftime(select_datetime, "%Y-%m-%d %H:%M:%S")
    
    (previous_datetime_str, previous_symbol) = get_previous_border_workday_intraday_rs(select_datetime_str, force_is_end)
    previous_datetime = datetime.datetime.strptime(previous_datetime_str, "%Y-%m-%d %H:%M:%S")
    if select_timezone is not None:
        previous_datetime = select_timezone.localize(previous_datetime)
    
    return (previous_datetime, previous_symbol)


def get_near_workday_intraday(select_datetime, is_after=True):
    """
    引数のdatetime.datetimeが営業日・営業時間の場合はそのまま，そうでない場合は最も近い境界を境界シンボルとともに返す．
    Paremeters
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
            "border_intra": 営業時間内
            "border_start": 営業時間の開始時刻
            "border_end": 営業時間の終了時刻
    """
    assert isinstance(select_datetime, datetime.datetime)
    select_timezone = get_timezone_from_datetime(select_datetime)
    if select_timezone is not None:
        select_datetime = select_datetime.replace(tzinfo=None)
    
    select_datetime_str = datetime.datetime.strftime(select_datetime, "%Y-%m-%d %H:%M:%S")
    
    (near_datetime_str, near_symbol) = get_near_workday_intraday_rs(select_datetime_str, is_after)
    near_datetime = datetime.datetime.strptime(near_datetime_str, "%Y-%m-%d %H:%M:%S")
    if select_timezone is not None:
        near_datetime = select_timezone.localize(near_datetime)
    
    return (near_datetime, near_symbol)


def add_workday_intraday_datetime(select_datetime, delta_time):
    """
    営業日・営業時間を考慮しdatetime.datetimeを減らす
    select_datetime: datetime.datetime
        指定する日時
    delta_time: datetime.timedelta
        加算するtimedelta(ミリ秒は切り捨て)
    """
    assert isinstance(select_datetime, datetime.datetime)
    assert delta_time >= timedelta(seconds=0)
    
    assert isinstance(select_datetime, datetime.datetime)
    select_timezone = get_timezone_from_datetime(select_datetime)
    if select_timezone is not None:
        select_datetime = select_datetime.replace(tzinfo=None)
    
    select_datetime_str = datetime.datetime.strftime(select_datetime, "%Y-%m-%d %H:%M:%S")
    delta_time_sec = int(delta_time.total_seconds())
    
    added_datetime_str = add_workday_intraday_datetime_rs(select_datetime_str, delta_time_sec)
    added_datetime = datetime.datetime.strptime(added_datetime_str, "%Y-%m-%d %H:%M:%S")
    
    if select_timezone is not None:
        added_datetime = select_timezone.localize(added_datetime)  
        
    return added_datetime


def sub_workday_intraday_datetime(select_datetime, delta_time):
    """
    営業日・営業時間を考慮しdatetime.datetimeを減らす
    select_datetime: datetime.datetime
        指定する日時
    delta_time: datetime.timedelta
        減算するtimedelta(ミリ秒は切り捨て)
    """
    assert isinstance(select_datetime, datetime.datetime)
    assert delta_time >= timedelta(seconds=0)
    
    assert isinstance(select_datetime, datetime.datetime)
    select_timezone = get_timezone_from_datetime(select_datetime)
    if select_timezone is not None:
        select_datetime = select_datetime.replace(tzinfo=None)
    
    select_datetime_str = datetime.datetime.strftime(select_datetime, "%Y-%m-%d %H:%M:%S")
    delta_time_sec = int(delta_time.total_seconds())
    
    subed_datetime_str = sub_workday_intraday_datetime_rs(select_datetime_str, delta_time_sec)
    subed_datetime = datetime.datetime.strptime(subed_datetime_str, "%Y-%m-%d %H:%M:%S")
    
    if select_timezone is not None:
        subed_datetime = select_timezone.localize(subed_datetime)  
        
    return subed_datetime


def get_timedelta_workdays_intraday(start_datetime, end_datetime):
    """
    指定期間中の営業日・営業時間をtimedelta(ミリ秒は切り捨て)として出力
    start_datetime: datetime.datetime
        指定期間の開始日時
    end_datetime: datetime.datetime
        指定期間の終了日時
    """
    assert isinstance(start_datetime, datetime.datetime)
    assert isinstance(end_datetime, datetime.datetime)
    
    select_timezone = get_timezone_from_datetime(start_datetime, end_datetime)
    if select_timezone is not None:
        start_datetime = start_datetime.replace(tzinfo=None)
        end_datetime = end_datetime.replace(tzinfo=None)
        
    start_datetime_str = datetime.datetime.strftime(start_datetime, "%Y-%m-%d %H:%M:%S")
    end_datetime_str = datetime.datetime.strftime(end_datetime, "%Y-%m-%d %H:%M:%S")
    
    delta_time_sec = get_timedelta_workdays_intraday_rs(start_datetime_str, end_datetime_str)
    
    return timedelta(seconds=delta_time_sec)


if __name__ == "__main__":
    pass