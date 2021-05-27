from pathlib import Path
import numpy as np
import pandas as pd
import datetime

from py_strict_list import StructureStrictList, strict_list_property

import sys
sys.path.append("E:/py_workdays_rs/py_workdays/rs_workdays/target/release")
from rs_workdays import set_range_holidays_rs

from py_workdays.scraping import all_make_source
#from .scraping import all_make_source


class CSVHolidayGetter:
    def __init__(self, csv_paths):
        if not isinstance(csv_paths, list):  # リストでないなら，リストにしておく
            csv_paths = [csv_paths]
            
        self.csv_paths = csv_paths
        
    def get_holidays(self, start_date, end_date, with_name=False):
        """
        期間を指定して祝日を取得．csvファイルを利用して祝日を取得している．
        start_date: datetime.date
            開始時刻のdate
        end_datetime: datetime.date
            終了時刻のdate
        with_name: bool
            休日の名前を出力するかどうか
        to_date: bool
            出力をdatetime.datetimeにするかdatetime.dateにするか
        """
        assert isinstance(start_date, datetime.date) and isinstance(end_date, datetime.date)
        assert not isinstance(start_date, datetime.datetime) and not isinstance(end_date, datetime.datetime)
        
        # datetime.dateをpd.Timestampに変換(datetime.dateは通常pd.DatetimeIndexと比較できないため)
        start_timestamp = pd.Timestamp(start_date)
        end_timestamp = pd.Timestamp(end_date)

        is_first = True
        is_multi = False

        for csv_path in self.csv_paths:
            if csv_path.exists():  # csvファイルが存在する場合
                holiday_df = pd.read_csv(csv_path, 
                                        header=None,
                                        names=["date", "holiday_name"],
                                        index_col="date",
                                        parse_dates=True
                                        )
            else:
                holiday_df = None

            if holiday_df is not None:
                if is_first:
                    left_df = holiday_df
                    is_first = False
                else:
                    is_multi = True

                if is_multi:
                    append_bool = ~holiday_df.index.isin(left_df.index)  # 左Dataframeに存在しない部分を追加
                    left_df = left_df.append(holiday_df.loc[append_bool])
                    left_df.sort_index(inplace=True)

        if is_first and not is_multi:  # 一度もNone以外が返ってこなかった場合
            if not with_name:  # 祝日名がいらない場合
                return np.array([])
            return np.array([[],[]])
        
        # 指定範囲内の祝日を取得
        holiday_in_span_index = (start_timestamp<=left_df.index)&(left_df.index<end_timestamp)
        holiday_in_span_df = left_df.loc[holiday_in_span_index]
        
        holiday_in_span_date_array = holiday_in_span_df.index.date
        holiday_in_span_name_array = holiday_in_span_df.loc[:,"holiday_name"].values
        holiday_in_span_array = np.stack([holiday_in_span_date_array,
                                          holiday_in_span_name_array
                                         ],
                                         axis=1
                                        )
        
        if not with_name:  # 祝日名がいらない場合
            return holiday_in_span_date_array
            
        return holiday_in_span_array


class Option():
    """
    オプションの指定のためのクラス
    holiday_start_year: int
        利用する休日の開始年
    holiday_end_year: int
        利用する休日の終了年
    backend: str
        休日取得のバックエンド．csvかjpholidayのいずれかが選べる
    csv_source_paths: list of str or pathlib.Path
        バックエンドをcsvにした場合の休日のソースcsvファイル
    holiday_weekdays: list of int
        休日曜日の整数のリスト
    intraday_borders: list of list of 2 datetime.time
        日中を指定する境界時間のリストのリスト
    """
    def __init__(self):
        self._holiday_start_year = datetime.datetime.now().year-5
        self._holiday_end_year = datetime.datetime.now().year
        
        self._backend = "csv"
        self._csv_source_paths = StructureStrictList(Path("py_workdays/source/holiday_naikaku.csv"))
        #self._csv_source_paths = StructureStrictList(Path(__file__).parent / Path("source/holiday_naikaku.csv"))
        self._csv_source_paths.hook_func.add(self.make_holidays)
        
        self.make_holiday_getter()  # HolidayGetterを作成
        self.make_holidays()  # アトリビュートに追加
        
        self._holiday_weekdays = StructureStrictList(5,6)  # 土曜日・日曜日
        self._intraday_borders = StructureStrictList([datetime.time(9,0), datetime.time(11,30)],
                                  [datetime.time(12,30), datetime.time(15,0)])
        
    csv_source_paths = strict_list_property("_csv_source_paths", include_outer_length=False)
    holiday_weekdays = strict_list_property("_holiday_weekdays", include_outer_length=False)
    intraday_borders = strict_list_property("_intraday_borders", include_outer_length=False)
    
    def make_holiday_getter(self):
        if self.backend == "csv":
            self._holiday_getter = CSVHolidayGetter(self.csv_source_paths)
        
    def make_holidays(self):
        """
        利用する休日のarrayとDatetimeIndexをアトリビュートとして作成．csv_pathを追加したときにも呼ぶ
        """
        self._holidays_date_array = self._holiday_getter.get_holidays(start_date=datetime.date(self.holiday_start_year,1,1),
                                                    end_date=datetime.date(self.holiday_end_year,12,31),
                                                    with_name=False,
                                                   )
        holidays_date_str_array = np.array([datetime.datetime.strftime(one_date, "%Y-%m-%d") for one_date in self._holidays_date_array])
        
        set_range_holidays_rs(holidays_date_str_array.tolist(), self._holiday_start_year, self._holiday_end_year)
        
    @property
    def holiday_start_year(self):
        return self._holiday_start_year
    
    @holiday_start_year.setter
    def holiday_start_year(self, year):
        assert isinstance(year,int)
        self._holiday_start_year = year
        self.make_holidays()  # アトリビュートに追加
    
    @property
    def holiday_end_year(self):
        return self._holiday_end_year

    @holiday_end_year.setter
    def holiday_end_year(self, year):
        assert isinstance(year,int)
        self._holiday_end_year = year
        self.make_holidays()  # アトリビュートに追加
    
    @property
    def backend(self):
        return self._backend
    
    @backend.setter
    def backend(self, backend_str):
        back_end_set = {"csv"}
        if backend_str not in back_end_set:
            raise Exception("backend must be in {}".format(back_end_set))
        self._backend = backend_str
        self.make_holiday_getter()  # HolidayGetterを作成
        self.make_holidays()  # 休日の作成
    
    @property
    def holidays_date_array(self):
        return self._holidays_date_array


# Optionの作成
option = Option()


def initialize_source():
    """
    csvのソースを初期化する．インストール時の開始時に呼ぶようにする．
    """
    all_make_source()
    option.__init__()  # optionの初期化


if __name__ == "__main__":
    pass