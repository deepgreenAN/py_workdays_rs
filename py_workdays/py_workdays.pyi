from typing import List, Set, Literal, Tuple, TypedDict, Any
from datetime import date, time, datetime, timedelta
import numpy as np
import numpy.typing as npt

Border = TypedDict("Border", {"start":time, "end":time})

def set_holidays_csvs(holidays_csv_paths: List[str], start_year: int, end_year: int) -> None:
    """
    csvを読み込んで利用できる祝日の更新をする  

    Parameters
    ----------
    - holidays_csv_paths: csvのパス
    - start_year: 利用する開始年(その年の1月1日から)
    - end_year: 利用する終了年(その年の12月31日まで)
    """
    ...

def set_range_holidays(holidays: List[date], start_year: int, end_year: int) -> None:
    """
    祝日のリストから祝日の更新をする

    Parameters
    ----------
    - holidays: 祝日のリスト
    - start_year: 利用する開始年(その年の1月1日から)
    - end_year: 利用する終了年(その年の12月31日まで)
    """
    ...

def add_range_holidays(holidays: List[date], start_year: int, end_year: int) -> None:
    """
    祝日のリストから祝日の追加をする

    Parameters
    ----------
    - holidays: 休日のリスト
    - start_year: 利用する開始年(その年の1月1日から)
    - end_year: 利用する終了年(その年の12月31日まで)
    """
    ...

def set_holiday_weekdays(holiday_weekday_numbers: Set[int]) -> None:
    """
    休日曜日の更新，曜日は月曜日が0で日曜日が6となる，

    Parameter
    ---------
    - new_one_holiday_weekday_set: 休日曜日のセット
    """
    ...

def set_intraday_borders(intraday_borders: List[Border]) -> None:
    """
    営業時間境界の更新  
    
    Parameter
    ---------
    - new_intrada_borders: 営業時間境界のリスト
    """
    ...

def get_range_holidays() -> List[date]:
    """
    祝日データの取得

    Return
    ------
    - 祝日のリスト
    """
    ...

def get_holiday_weekdays() -> Set[int]:
    """
    休日曜日データの取得，曜日は月曜日が0で日曜日が6となる，

    Return
    ------
    - 休日曜日のset
    """
    ...

def get_intraday_borders() -> List[Border]:
    """
    営業時間境界の取得

    Return
    ------
    - 営業時間境界のリスト
        - "start": 開始時間
        - "end": 終了時間
    """
    ...

def make_source_naikaku(source_csv_path: str) -> None:
    """
    内閣府のデータを指定したパスにソースとして保存

    Parameters
    - source_csv_path: 保存するcsvのパス
    """
    ...

def request_holidays_naikaku(start_year: int, end_year: int) -> None:
    """
    内閣府による祝日データを取得して祝日に設定する(同期)(feature!="wasm")

    Parameters
    ----------
    - start_year=2016: 利用範囲の開始年
    - end_year=2025: 利用範囲の終了年
    """
    ...

def get_workdays(
    start_date: date, 
    end_date: date, 
    closed: Literal["left", "right", "both", "not"] = "left"
    ) -> List[date]:
    """
    start_dateからend_dateまでの営業日を取得 

    Parameters
    ----------
    - start_date: 開始日
    - end_date: 終了日
    - closed="left": 境界を含めるかどうか
        - "left": 終了境界を含めない
        - "right": 開始境界を含めない
        - "not": どちらの境界も含める
        - "both": どちらの境界も含めない

    Return
    ------ 
    - 営業日のリスト
    """
    ...

def check_workday(select_date: date) -> bool:
    """
    select_dateが営業日であるか判定

    Parameter
    ---------
    - select_date: 指定する日

    Return
    ------
    - 営業日であるかどうか
    """
    ...

def get_next_workday(select_date: date, days: int=1) -> date:
    """
    select_dateからdays分の次の営業日を取得  

    Parameters
    ----------
    - select_date: 指定する日
    - days=1: 進める日数 

    Return
    ------
    - 次の営業日
    """
    ...

def get_previous_workday(select_date: date, days: int=1) -> date:
    """
    select_dateからdays分の前の営業日を取得

    Parameters
    ----------
    - select_date: 指定する日
    - days=1: 減らす日数

    Return
    ------
    - 前の営業日
    """
    ...

def get_near_workday(select_date: date, is_after:bool=True) -> date:
    """
    最近の営業日を取得

    Parameters
    ----------
    - select_date: 指定する日
    - is_after: 後の営業日を所得するかどうか

    Return
    ------
    - 最近の営業日
    """
    ...

def get_workdays_number(select_date: date, days: int) -> List[date]:
    """
    start_dateからdays分だけの営業日のリストを取得

    Parameters
    ----------
    - start_date: 開始日
    - days: 日数

    Return
    ------
    営業日のリスト
    """
    ...

def check_workday_intraday_naive(select_datetime: date) -> bool:
    """
    select_datetimeが営業日・営業時間内であるかどうかを判定．naiveを前提とする

    Parameters
    ----------
    - select_datetime: 指定する日時

    Return
    ------
    - 営業日・営業時間内であるかどうか
    """
    ...

def get_next_border_workday_intraday_naive(
        select_datetime: datetime
    ) -> Tuple[datetime, str]:
    """
    次の営業日・営業時間内のdatetimeをその状態とともに取得．naiveを前提とする

    Parameter
    ---------
    - select_datetime: 指定する日時

    Returns
    -------
    - 次の営業日・営業時間内のdatetime
    - 状態を示す文字列
        - 'border_start': 営業時間の開始
        - 'border_end': 営業時間の終了
    """
    ...

def get_previous_border_workday_intraday_naive(
        select_datetime: datetime, 
        force_is_end: bool=False
    ) -> Tuple[datetime, str]:
    """
    前の営業日・営業時間内のdatetimeをその状態とともに取得

    Parameter
    ---------
    - select_datetime: 指定する日時
    - fore_is_end: 終了時間のときに次の終了時間を取得するかどうか

    Returns
    - 前の営業日・営業時間内のdatetime
    - 状態を示す文字列
        - 'border_start': 営業時間の開始
        - 'border_end': 営業時間の終了
    """
    ...

def get_near_workday_intraday_naive(
        select_datetime: datetime, 
        is_after:bool=True
    ) -> Tuple[datetime, str]:
    """
    最近の営業日・営業時間内のdatetimeをその状態とともに取得．select_datetimeが営業日・営業時間内の場合そのまま返る．  

    Parameters
    ----------
    - select_datetime: 指定する日時
    - is_after: 後ろを探索するかどうか

    Returns
    -------
    - 前の営業日・営業時間内のdatetime
    - 状態を示す文字列
        - 'border_intra': 営業時間内
        - 'border_start': 営業時間の開始
        - 'border_end': 営業時間の終了
    """
    ...

def add_workday_intraday_datetime_naive(
    select_datetime: datetime, 
    delta_time: timedelta
    ) -> datetime:
    """
    営業日・営業時間を考慮しDateTimeを加算する．(負の値も可能)
    1秒より小さい単位は無視される

    Parameters
    ----------
    - select_datetime: 指定する日時
    - dela_time: 加算するtimedelta

    Return
    ------
    加算された日時
    """
    ...

def get_timedelta_workdays_intraday_naive(
    start_datetime_vec: datetime, 
    end_datetime_vec: datetime
    ) -> timedelta:
    """
    start_datetimeからend_datetimeの営業日・営業時間のtimedeltaを取得
    1秒より小さい単位は無視される

    Parameters
    ----------
    - start_datetime: 開始日時
    - end_datetime: 終了日時

    Return
    ------
    営業日・営業時間のtimedelta
    """
    ...

def extract_workdays_bool_naive(int_64_numpy: npt.NDArray[np.int64]) -> npt.NDArray[np.bool_]:
    """
    np.int64のndarrayから営業日のものをboolとして抽出  

    Parameters
    ----------
    - datetime_64_numpy: np.ndarray(dtype=datetime64) 
        抽出したい日時のndarray
    
    Return
    ------
    - ブールのndarray: np.ndarray(dtype=bool)
    """
    ...

def extract_intraday_bool_naive(int_64_numpy: npt.NDArray[np.int64]) -> npt.NDArray[np.bool_]:
    """
    np.int64のndarrayから営業時間のものをboolとして抽出
    
    Parameters
    ----------
    - datetime_64_numpy: np.ndarray(dtype=datetime64) 
        抽出したい日時のndarray
    
    Return
    ------
    - ブールのndarray: np.ndarray(dtype=bool)
    """
    ...

def extract_workdays_intraday_bool_naive(int_64_numpy: npt.NDArray[np.int64]) -> npt.NDArray[np.bool_]:
    """
    np.int64のndarrayから営業日・営業時間のものをboolとして抽出

    Parameters
    ----------
    - datetime_64_numpy: np.ndarray(dtype=datetime64) 
        抽出したい日時のndarray
    
    Return
    ------
    - ブールのndarray: np.ndarray(dtype=bool)
    """
    ...

class PyWorkdaysError(Exception):
    """
    pyworkdaysのrust部分内部で起こるエラー
    """
    def __init__(self, *args: List[Any]) -> None:
        """
        初期化メソッド
        """
        ...



