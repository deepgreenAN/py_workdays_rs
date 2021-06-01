import unittest
import numpy as np
import datetime
from datetime import timedelta
import pandas as pd
from pathlib import Path
from pytz import timezone
from typing import NoReturn

from py_workdays import get_workdays, get_not_workdays
from py_workdays import check_workday, get_next_workday, get_previous_workday, get_workdays_number, get_near_workday
from py_workdays import extract_workdays, extract_intraday, extract_workdays_intraday, extract_workdays_intraday_index
from py_workdays import check_workday_intraday, get_near_workday_intraday, get_next_border_workday_intraday, get_previous_border_workday_intraday
from py_workdays import add_workday_intraday_datetime, sub_workday_intraday_datetime, get_timedelta_workdays_intraday
from py_workdays import option


def true_holidays_2021() -> np.ndarray:
    holidays_list = [datetime.date(2021,1,1),
                     datetime.date(2021,1,11),
                     datetime.date(2021,2,11),
                     datetime.date(2021,2,23),
                     datetime.date(2021,3,20),
                     datetime.date(2021,4,29),
                     datetime.date(2021,5,3),
                     datetime.date(2021,5,4),
                     datetime.date(2021,5,5),
                     datetime.date(2021,7,22),
                     datetime.date(2021,7,23),
                     datetime.date(2021,8,8),
                     datetime.date(2021,8,9),  #振替
                     datetime.date(2021,9,20),
                     datetime.date(2021,9,23),
                     datetime.date(2021,11,3),
                     datetime.date(2021,11,23)
                    ]

    return np.array(holidays_list)


class TestWorkdays(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        option.holiday_start_year = 2021
        option.holiday_weekdays = [5,6]
        option.intraday_borders = [[datetime.time(9,0), datetime.time(11,30)],
                                   [datetime.time(12,30), datetime.time(15,0)]]
        
        
    def test_related_workdays(self) -> None:
        # get_workdays, get_not_workdays
        all_date = pd.date_range(datetime.date(2021,1,1), datetime.date(2021,12,31), freq="D").date
        all_weekdays = np.array([item.weekday() for item in all_date])
        
        is_hoildays = np.in1d(all_date, true_holidays_2021())  # 祝日
        is_hoilday_weekdays = np.logical_or.reduce([all_weekdays==holiday_weekday for holiday_weekday in option.holiday_weekdays])  # 祝日曜日
        
        is_not_workdays = is_hoildays | is_hoilday_weekdays
        is_workdays = (~is_hoildays) & (~is_hoilday_weekdays)
        
        true_not_workdays = all_date[is_not_workdays]
        true_workdays = all_date[is_workdays]
        
        workdays_array = get_workdays(datetime.date(2021,1,1), datetime.date(2022,1,1))
        not_workdays_array = get_not_workdays(datetime.date(2021,1,1), datetime.date(2022,1,1))
        
        self.assertTrue(np.array_equal(workdays_array, true_workdays))
        self.assertTrue(np.array_equal(not_workdays_array, true_not_workdays))
        
        # get_workdays_number
        # 祝日始まり
        workdays_50_array = get_workdays_number(datetime.date(2021,1,1), 50)
        self.assertTrue(np.array_equal(workdays_50_array, true_workdays[:50]))
        
        # 営業日始まり
        workdays_50_array = get_workdays_number(datetime.date(2021,1,4), 50)  # 1月4日は一番最初の営業日
        self.assertTrue(np.array_equal(workdays_50_array, true_workdays[:50]))
        
        # check_workday
        checked_workdays = [check_workday(one_date) for one_date in true_workdays]
        self.assertTrue(all(checked_workdays))
        checked_not_workdays = [check_workday(one_date) for one_date in true_not_workdays]
        self.assertFalse(any(checked_not_workdays))
        
        # get_next_workday
        #from IPython.core.debugger import Pdb; Pdb().set_trace()
        # 祝日始まり
        workdays_array = np.array([get_next_workday(datetime.date(2021,1,1), i) for i in range(1,len(true_workdays)+1)])
        self.assertTrue(np.array_equal(workdays_array, true_workdays))
        # 営業日始まり
        workdays_array = np.array([get_next_workday(datetime.date(2021,1,4), i) for i in range(1,len(true_workdays))])
        self.assertTrue(np.array_equal(workdays_array, true_workdays[1:]))   # get_next_workdaysは初日は含めないので
        
        # get_previous_workday
        # 祝日始まり
        workdays_array = np.array([get_previous_workday(datetime.date(2022,1,1), i) for i in range(1,len(true_workdays)+1)])
        self.assertTrue(np.array_equal(workdays_array[::-1], true_workdays))
        # 営業日始まり
        workdays_array = np.array([get_previous_workday(datetime.date(2021,12,31), i) for i in range(1,len(true_workdays))])
        self.assertTrue(np.array_equal(workdays_array[::-1], true_workdays[:-1]))
        
        # get_near_workday
        near_workday = get_near_workday(datetime.date(2021,1,1), is_after=True)
        self.assertEqual(near_workday, datetime.date(2021,1,4))
        near_workday = get_near_workday(datetime.date(2021,1,1), is_after=False)
        self.assertEqual(near_workday, datetime.date(2020,12,31))
        
    def test_related_extract(self) -> None:
        all_date = pd.date_range(datetime.date(2021,1,1), datetime.date(2021,12,31), freq="D").date
        all_weekdays = np.array([item.weekday() for item in all_date])
        
        is_hoildays = np.in1d(all_date, true_holidays_2021())  # 祝日
        is_hoilday_weekdays = np.logical_or.reduce([all_weekdays==holiday_weekday for holiday_weekday in option.holiday_weekdays])  # 祝日曜日
        
        is_not_workdays = is_hoildays | is_hoilday_weekdays
        
        true_not_workdays = all_date[is_not_workdays] 
        
        
        dt_index = pd.date_range(datetime.datetime(2021,1,1,0,0,0), datetime.datetime(2021,12,31,23,59,0), freq="T")
        nan_df = pd.DataFrame(None, index=dt_index)
        nan_df["column1"] = np.nan
        extracted_df = extract_workdays(nan_df)
        # 抽出したpd.DataFrameのdateが非営業日に含まれない
        self.assertFalse(np.any(np.in1d(extracted_df.index.date, true_not_workdays)))
        
        # 日中以外のある時間のデータの長さが0
        extracted_df = extract_intraday(nan_df)
        self.assertEqual(len(extracted_df.at_time(datetime.time(8,0)).index),0)
        
        # 両方チェック
        jst = timezone("Asia/Tokyo")
        nan_df.index = nan_df.index.tz_localize(jst)
        extracted_df = extract_workdays_intraday(nan_df)
        self.assertFalse(np.any(np.in1d(extracted_df.index.date, true_not_workdays)))
        self.assertEqual(len(extracted_df.at_time(datetime.time(8,0)).index),0)
    
    def test_related_datetime_raw(self) -> None:        
        # check_workday_intraday
        self.assertTrue(check_workday_intraday(datetime.datetime(2021,1,4,10,0,0)))
        self.assertFalse(check_workday_intraday(datetime.datetime(2021,1,1,10,0,0)))
        self.assertFalse(check_workday_intraday(datetime.datetime(2021,1,4,0,0,0)))
        
        # get_next_border_workday_intraday
        next_border_workday_intraday_tuple = get_next_border_workday_intraday(datetime.datetime(2021,1,1,10,0,0))
        self.assertEqual(next_border_workday_intraday_tuple, (datetime.datetime(2021, 1, 4, 9, 0), 'border_start'))
        next_border_workday_intraday_tuple = get_next_border_workday_intraday(datetime.datetime(2021,1,4,9,0,0))
        self.assertEqual(next_border_workday_intraday_tuple, (datetime.datetime(2021, 1, 4, 11, 30), 'border_end'))
        next_border_workday_intraday_tuple = get_next_border_workday_intraday(datetime.datetime(2021,1,4,11,30,0))
        self.assertEqual(next_border_workday_intraday_tuple, (datetime.datetime(2021, 1, 4, 12, 30), 'border_start'))
        
        # get_previous_border_workday_intraday
        previous_border_workday_intraday_tuple = get_previous_border_workday_intraday(datetime.datetime(2021,1,1,10,0,0))
        self.assertEqual(previous_border_workday_intraday_tuple, (datetime.datetime(2020, 12, 31, 15, 0), 'border_end'))
        previous_border_workday_intraday_tuple = get_previous_border_workday_intraday(datetime.datetime(2021,12,31,12,30,0))
        self.assertEqual(previous_border_workday_intraday_tuple, (datetime.datetime(2021, 12, 31, 11, 30), 'border_end'))       
        previous_border_workday_intraday_tuple = get_previous_border_workday_intraday(datetime.datetime(2021,12,31,15,0,0))
        self.assertEqual(previous_border_workday_intraday_tuple, (datetime.datetime(2021, 12, 31, 15, 0), 'border_end'))
        previous_border_workday_intraday_tuple = get_previous_border_workday_intraday(datetime.datetime(2021,12,31,15,0,0), force_is_end=True)
        self.assertEqual(previous_border_workday_intraday_tuple, (datetime.datetime(2021, 12, 31, 12, 30), 'border_start'))
        
        # get_near_workday_ntraday
        near_workday_intraday_tuple = get_near_workday_intraday(datetime.datetime(2021,1,1,10,0,0), is_after=True)
        self.assertEqual((datetime.datetime(2021,1,4,9,0,0), "border_start"), near_workday_intraday_tuple)
        near_workday_intraday_tuple = get_near_workday_intraday(datetime.datetime(2021,1,1,10,0,0), is_after=False)
        self.assertEqual((datetime.datetime(2020,12,31,15,0,0), "border_end"), near_workday_intraday_tuple)
                
        # add_workday_intraday_datetime
        datetime_range = pd.date_range(start=datetime.datetime(2021,1,1,0,0,0), end=datetime.datetime(2021,2,1,0,0,0), closed="left", freq="5T")
        extracted_datetime_range: pd.DatetimeIndex = extract_workdays_intraday_index(datetime_range)
        extracted_datetime_range_array = extracted_datetime_range.to_pydatetime()
        
        datetime_list = [datetime.datetime(2021, 1, 4, 9, 0)]
        for i in range(1,len(extracted_datetime_range)):
            datetime_list.append(add_workday_intraday_datetime(datetime.datetime(2021, 1, 1, 0, 0), timedelta(minutes=5)*i))
        addded_dateteime_array = np.array(datetime_list)
        self.assertTrue(np.array_equal(extracted_datetime_range_array, addded_dateteime_array))
        
        # sub_workday_intraday_datetime
        datetime_list = []
        for i in range(1,len(extracted_datetime_range)+1):
            datetime_list.append(sub_workday_intraday_datetime(datetime.datetime(2021, 2, 1, 0, 0), timedelta(minutes=5)*i))
        subed_dateteime_array = np.array(datetime_list[::-1])
        self.assertTrue(np.array_equal(extracted_datetime_range_array, subed_dateteime_array))
        
        # get_timedelta_workdays_intraday
        start_datetime = datetime.datetime(2021,1,4,9,0,0)
        end_datetime = datetime.datetime(2021,12,31,9,0,0)
        delta_time = get_timedelta_workdays_intraday(start_datetime, end_datetime)
        self.assertEqual(datetime.datetime(2021,12,31,9,0,0), add_workday_intraday_datetime(start_datetime, delta_time))
        
        start_datetime = datetime.datetime(2021,1,4,14,0,0)
        end_datetime = datetime.datetime(2021,12,31,10,0,0)
        delta_time = get_timedelta_workdays_intraday(start_datetime, end_datetime)
        self.assertEqual(datetime.datetime(2021,12,31,10,0,0), add_workday_intraday_datetime(start_datetime, delta_time))
        
        start_datetime = datetime.datetime(2021,1,4,15,0,0)
        end_datetime = datetime.datetime(2021,12,31,15,0,0)
        delta_time = get_timedelta_workdays_intraday(start_datetime, end_datetime)
        self.assertEqual(datetime.datetime(2022, 1, 3, 9, 0), add_workday_intraday_datetime(start_datetime, delta_time))
        
        start_datetime = datetime.datetime(2021,1,4,14,0,0)
        end_datetime = datetime.datetime(2021,12,31,15,0,0)
        delta_time = get_timedelta_workdays_intraday(start_datetime, end_datetime)
        self.assertEqual(datetime.datetime(2021,1,4,14,0,0), sub_workday_intraday_datetime(end_datetime, delta_time))
        
        start_datetime = datetime.datetime(2021,1,4,10,0,0)
        end_datetime = datetime.datetime(2021,12,31,14,0,0)
        delta_time = get_timedelta_workdays_intraday(start_datetime, end_datetime)
        self.assertEqual(datetime.datetime(2021,1,4,10,0,0), sub_workday_intraday_datetime(end_datetime, delta_time))
        
        start_datetime = datetime.datetime(2021,1,4,9,0,0)
        end_datetime = datetime.datetime(2021,12,31,9,0,0)
        delta_time = get_timedelta_workdays_intraday(start_datetime, end_datetime)
        self.assertEqual(datetime.datetime(2021,1,4,9,0,0), sub_workday_intraday_datetime(end_datetime, delta_time))
        
    def test_related_datetime_jst(self) -> None:
        jst = timezone("Asia/Tokyo")
        
        # check_workday_intraday
        self.assertTrue(check_workday_intraday(jst.localize(datetime.datetime(2021,1,4,10,0,0))))
        self.assertFalse(check_workday_intraday(jst.localize(datetime.datetime(2021,1,1,10,0,0))))
        self.assertFalse(check_workday_intraday(jst.localize(datetime.datetime(2021,1,4,0,0,0))))
        
        # get_next_border_workday_intraday
        next_border_workday_intraday_tuple = get_next_border_workday_intraday(jst.localize(datetime.datetime(2021,1,1,10,0,0)))
        self.assertEqual(next_border_workday_intraday_tuple, (jst.localize(datetime.datetime(2021, 1, 4, 9, 0)), 'border_start'))
        next_border_workday_intraday_tuple = get_next_border_workday_intraday(jst.localize(datetime.datetime(2021,1,4,9,0,0)))
        self.assertEqual(next_border_workday_intraday_tuple, (jst.localize(datetime.datetime(2021, 1, 4, 11, 30)), 'border_end'))
        next_border_workday_intraday_tuple = get_next_border_workday_intraday(jst.localize(datetime.datetime(2021,1,4,11,30,0)))
        self.assertEqual(next_border_workday_intraday_tuple, (jst.localize(datetime.datetime(2021, 1, 4, 12, 30)), 'border_start'))
        
        # get_previous_border_workday_intraday
        previous_border_workday_intraday_tuple = get_previous_border_workday_intraday(jst.localize(datetime.datetime(2021,1,1,10,0,0)))
        self.assertEqual(previous_border_workday_intraday_tuple, (jst.localize(datetime.datetime(2020, 12, 31, 15, 0)), 'border_end'))
        previous_border_workday_intraday_tuple = get_previous_border_workday_intraday(jst.localize(datetime.datetime(2021,12,31,12,30,0)))
        self.assertEqual(previous_border_workday_intraday_tuple, (jst.localize(datetime.datetime(2021, 12, 31, 11, 30)), 'border_end'))
        previous_border_workday_intraday_tuple = get_previous_border_workday_intraday(jst.localize(datetime.datetime(2021,12,31,15,0,0)))
        self.assertEqual(previous_border_workday_intraday_tuple, (jst.localize(datetime.datetime(2021, 12, 31, 15, 0)), 'border_end'))
        previous_border_workday_intraday_tuple = get_previous_border_workday_intraday(jst.localize(datetime.datetime(2021,12,31,15,0,0)), force_is_end=True)
        self.assertEqual(previous_border_workday_intraday_tuple, (jst.localize(datetime.datetime(2021, 12, 31, 12, 30)), 'border_start'))
        
        # get_near_workday_ntraday
        near_workday_intraday_tuple = get_near_workday_intraday(jst.localize(datetime.datetime(2021,1,1,10,0,0)), is_after=True)
        self.assertEqual((jst.localize(datetime.datetime(2021,1,4,9,0,0)), "border_start"), near_workday_intraday_tuple)
        near_workday_intraday_tuple = get_near_workday_intraday(jst.localize(datetime.datetime(2021,1,1,10,0,0)), is_after=False)
        self.assertEqual((jst.localize(datetime.datetime(2020,12,31,15,0,0)), "border_end"), near_workday_intraday_tuple)
                
        # add_workday_intraday_datetime
        datetime_range = pd.date_range(start=jst.localize(datetime.datetime(2021,1,1,0,0,0)), end=jst.localize(datetime.datetime(2021,2,1,0,0,0)), closed="left", freq="5T")
        extracted_datetime_range: pd.DatetimeIndex = extract_workdays_intraday_index(datetime_range)
        extracted_datetime_range_array = extracted_datetime_range.to_pydatetime()
        
        datetime_list = [jst.localize(datetime.datetime(2021, 1, 4, 9, 0))]
        for i in range(1,len(extracted_datetime_range)):
            datetime_list.append(add_workday_intraday_datetime(jst.localize(datetime.datetime(2021, 1, 1, 0, 0)), timedelta(minutes=5)*i))
        addded_dateteime_array = np.array(datetime_list)
        self.assertTrue(np.array_equal(extracted_datetime_range_array, addded_dateteime_array))
        
        # sub_workday_intraday_datetime
        datetime_list = []
        for i in range(1,len(extracted_datetime_range)+1):
            datetime_list.append(sub_workday_intraday_datetime(jst.localize(datetime.datetime(2021, 2, 1, 0, 0)), timedelta(minutes=5)*i))
        subed_dateteime_array = np.array(datetime_list[::-1])
        self.assertTrue(np.array_equal(extracted_datetime_range_array, subed_dateteime_array))
        
        # get_timedelta_workdays_intraday
        start_datetime = jst.localize(datetime.datetime(2021,1,4,9,0,0))
        end_datetime = jst.localize(datetime.datetime(2021,12,31,9,0,0))
        delta_time = get_timedelta_workdays_intraday(start_datetime, end_datetime)
        self.assertEqual(jst.localize(datetime.datetime(2021,12,31,9,0,0)), add_workday_intraday_datetime(start_datetime, delta_time))
        
        start_datetime = jst.localize(datetime.datetime(2021,1,4,14,0,0))
        end_datetime = jst.localize(datetime.datetime(2021,12,31,10,0,0))
        delta_time = get_timedelta_workdays_intraday(start_datetime, end_datetime)
        self.assertEqual(jst.localize(datetime.datetime(2021,12,31,10,0,0)), add_workday_intraday_datetime(start_datetime, delta_time))
        
        start_datetime = jst.localize(datetime.datetime(2021,1,4,15,0,0))
        end_datetime = jst.localize(datetime.datetime(2021,12,31,15,0,0))
        delta_time = get_timedelta_workdays_intraday(start_datetime, end_datetime)
        self.assertEqual(jst.localize(datetime.datetime(2022, 1, 3, 9, 0)), add_workday_intraday_datetime(start_datetime, delta_time))
        
        start_datetime = jst.localize(datetime.datetime(2021,1,4,14,0,0))
        end_datetime = jst.localize(datetime.datetime(2021,12,31,15,0,0))
        delta_time = get_timedelta_workdays_intraday(start_datetime, end_datetime)
        self.assertEqual(jst.localize(datetime.datetime(2021,1,4,14,0,0)), sub_workday_intraday_datetime(end_datetime, delta_time))
        
        start_datetime = jst.localize(datetime.datetime(2021,1,4,10,0,0))
        end_datetime = jst.localize(datetime.datetime(2021,12,31,14,0,0))
        delta_time = get_timedelta_workdays_intraday(start_datetime, end_datetime)
        self.assertEqual(jst.localize(datetime.datetime(2021,1,4,10,0,0)), sub_workday_intraday_datetime(end_datetime, delta_time))
        
        start_datetime = jst.localize(datetime.datetime(2021,1,4,9,0,0))
        end_datetime = jst.localize(datetime.datetime(2021,12,31,9,0,0))
        delta_time = get_timedelta_workdays_intraday(start_datetime, end_datetime)
        self.assertEqual(jst.localize(datetime.datetime(2021,1,4,9,0,0)), sub_workday_intraday_datetime(end_datetime, delta_time))     


class TestOption(unittest.TestCase):
    def test_make_workdays(self) -> None:
        #optionを設定するだけで休日が更新される．
        option.holiday_start_year = 2021
        option.holiday_end_year = 2021
        self.assertTrue(np.array_equal(option.holidays_date_array, true_holidays_2021()))
        
    def test_append_source_path(self) -> None:
        option.backend = "csv"
        temp_source_path = Path("py_workdays/source/temp.csv")
        # 存在しない祝日を記したcsvファイルを追加
        dt_index = pd.DatetimeIndex([datetime.date(1900,1,1)])
        new_holiday_df = pd.DataFrame({"holiday_name":["元日"]}, index=dt_index)
        new_holiday_df.to_csv(temp_source_path, header=False)
        
        option.holiday_start_year = 1900  # このタイミングで1900年にしておく
        
        option.csv_source_paths.append(temp_source_path)  # csvパスを追加
        self.assertEqual(option.holidays_date_array[0],datetime.date(1900,1,1))
        
        temp_source_path.unlink()

if __name__ == "__main__":
    unittest.main()