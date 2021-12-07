import datetime
from pathlib import Path
from typing import List, Dict
from datetime import time, date

from py_strict_list import StructureStrictList, strict_list_property

from .py_workdays import set_holidays_csvs, set_intraday_borders, set_holiday_weekdays, make_source_naikaku, add_range_holidays, get_range_holidays

def initialize_source() -> None:
    """
    内閣府のサイトから祝日データを取得し"../source/holiday_naikaku.csv"に保存
    """
    source_path = Path(__file__).parent / Path("source/holiday_naikaku.csv")
    if not source_path.exists():
        make_source_naikaku(str(source_path))

class Config():
    """
    動的に変更できる祝日データの設定
    """
    def __init__(self) -> None:
        self.initialize_config()

    def initialize_config(self) -> None:
        """
        祝日データの設定の初期化
        """
        self._holiday_start_year: int = datetime.datetime.now().year - 5
        self._holiday_end_year: int = datetime.datetime.now().year + 2

        self._csv_source_paths = StructureStrictList(Path(__file__).parent / Path("source/holiday_naikaku.csv"))
        self._csv_source_paths.hook_func.add(self._set_holidays)  # 変更にフック

        self._holiday_weekdays = StructureStrictList(5, 6)
        self._holiday_weekdays.hook_func.add(self._set_holiday_weekdays)  # 変更にフック

        self._intraday_borders = StructureStrictList(
            {"start": time(9, 0), "end": time(11, 30)},
            {"start": time(12, 30), "end": time(15, 0)}
        )
        self._intraday_borders.hook_func.add(self._set_intraday_borders)  # 変更にフック
        
        self._set_holidays()
        self._set_holiday_weekdays()
        self._set_intraday_borders()

    csv_source_paths = strict_list_property("_csv_source_paths", include_outer_length=False)
    holiday_weekdays = strict_list_property("_holiday_weekdays", include_outer_length=False)
    intraday_borders = strict_list_property("_intraday_borders", include_outer_length=False)



    def _set_holidays(self) -> None:
        """
        csvソースから祝日データを読み込む
        """
        holidays_csv_path_strs = [str(one_path.resolve()) for one_path in self._csv_source_paths if one_path.exists()]
        
        set_holidays_csvs(
            holidays_csv_path_strs,
            self._holiday_start_year,
            self._holiday_end_year
        )

    def _set_holiday_weekdays(self) -> None:
        """
        休日曜日を設定
        """
        holiday_weekdays = set(list(self._holiday_weekdays))
        set_holiday_weekdays(holiday_weekdays)


    def _set_intraday_borders(self) -> None:
        """
        営業時間の境界を設定
        """
        intraday_borders = list(self._intraday_borders)
        set_intraday_borders(intraday_borders)

    @property
    def holiday_start_year(self) -> int:
        return self._holiday_start_year

    @holiday_start_year.setter
    def holiday_start_year(self, year: int) -> None:
        assert(isinstance(year, int))
        self._holiday_start_year = year
        self._set_holidays()

    @property
    def holiday_end_year(self) -> int:
        return self._holiday_end_year

    @holiday_end_year.setter
    def holiday_end_year(self, year: int) -> None:
        assert(isinstance(year, int))
        self._holiday_end_year = year
        self._set_holidays()

    def add_range_holidays(self, range_holidays: List[date]) -> None:
        """
        祝日を追加
        """
        add_range_holidays(
            range_holidays,
            self._holiday_start_year,
            self._holiday_end_year
        )

    @property
    def range_holidays(self) -> List[date]:
        """
        祝日データを取得
        """
        return get_range_holidays()

initialize_source()
config = Config()


if __name__ == "__main__":
    pass