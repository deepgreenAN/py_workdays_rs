use std::collections::{HashSet, HashMap};
use chrono::Weekday;

use pyo3::prelude::*;
use pyo3::wrap_pyfunction;
use pyo3::types::{PyDate, PyDateTime, PyTime, PyDelta};
use pyo3::create_exception;
use numpy::{IntoPyArray, PyArray, PyReadonlyArray, Ix1};
use numpy::ndarray::{Array};

use chrono::{NaiveDate, NaiveDateTime};
use num_traits::cast::FromPrimitive;

mod convert;
mod error;

use crate::convert::*;
use crate::error::Error;

// PyErrとしてPyWorkdaysErrorを定義
create_exception!(module, PyWorkdaysError, pyo3::exceptions::PyException);

// crate::error::ErrorをPyErrに変換できるようにする(pyfunctionが認識できる)
impl std::convert::From<Error> for PyErr {
    fn from(err: Error) -> PyErr {
        PyWorkdaysError::new_err(err.to_string())
    }
}

/// csvを読み込んで利用できる祝日の更新をする  
/// Argments
/// - holidays_csv_paths: csvのパス
/// - start_year: 利用する開始年(その年の1月1日から)
/// - end_year: 利用する終了年(その年の12月31日まで)
#[pyfunction]
fn set_holidays_csvs(
    holidays_csv_paths: Vec<String>, 
    start_year: i32, 
    end_year: i32
) -> Result<(), Error> {
    rs_workdays::set_holidays_csvs(&holidays_csv_paths, start_year, end_year)?;
    Ok(())
}

/// 祝日のリストから祝日の更新をする  
/// Argments
/// - holidays: 祝日のリスト
/// - start_year: 利用する開始年(その年の1月1日から)
/// - end_year: 利用する終了年(その年の12月31日まで)
#[pyfunction]
fn set_range_holidays(
    holidays: Vec<&PyDate>, 
    start_year: i32, 
    end_year: i32
) -> Result<(), Error> {
    let holidays: Vec<NaiveDate> = holidays.iter()
        .map(|py_date|{date_py_to_chrono(*py_date)}).collect();
    rs_workdays::set_range_holidays(&holidays, start_year, end_year);
    Ok(())
}

/// 祝日のリストから祝日の追加をする  
/// Argments
/// - holidays: 休日のリスト
/// - start_year: 利用する開始年(その年の1月1日から)
/// - end_year: 利用する終了年(その年の12月31日まで)
#[pyfunction]
fn add_range_holidays(
    holidays: Vec<&PyDate>,
    start_year: i32,
    end_year: i32
) -> Result<(), Error> {
    let holidays: Vec<NaiveDate> = holidays.iter()
        .map(|py_date| {date_py_to_chrono(*py_date)}).collect();
    rs_workdays::add_range_holidays(&holidays, start_year, end_year);
    Ok(())
}

/// 休日曜日の更新  
/// Argment
/// - new_one_holiday_weekday_set: 休日曜日のセット
#[pyfunction]
fn set_holiday_weekdays(holiday_weekday_numbers: HashSet<usize>) -> Result<(), Error> {
    let holiday_weekday_set: HashSet<Weekday> = holiday_weekday_numbers.iter()
        .map(|day_number|{
            Weekday::from_usize(*day_number).unwrap()
        }).collect();
    rs_workdays::set_holiday_weekdays(&holiday_weekday_set);
    Ok(())
}

/// 営業時間境界の更新  
/// Argment
/// - new_intrada_borders: 営業時間境界のベクター
#[pyfunction]
fn set_intraday_borders(intraday_borders: Vec<HashMap<&str, &PyTime>>) -> Result<(), Error> {
    let time_borders: Vec<rs_workdays::global::TimeBorder> = intraday_borders.iter()
        .map(|dict|{
            let start_time = dict.get(&"start")
                .ok_or(Error::ArgKeyError{arg_name: "intraday_borders".to_string(), key_name: "start".to_string()})?;
            let end_time = dict.get(&"end")
                .ok_or(Error::ArgKeyError{arg_name: "intraday_borders".to_string(), key_name: "end".to_string()})?;
            Ok(
                rs_workdays::global::TimeBorder {
                    start: time_py_to_chrono(*start_time),
                    end: time_py_to_chrono(*end_time)
                }
            )
        }).collect::<Result<Vec<rs_workdays::global::TimeBorder>, Error>>()?;
    rs_workdays::set_intraday_borders(&time_borders);
    Ok(())
}

/// 祝日データの取得  
/// Return
/// - 祝日のリスト
#[pyfunction]
fn get_range_holidays<'p>(py: Python<'p>) -> Result<Vec<&'p PyDate>, Error> {
    let range_holidays = rs_workdays::get_range_holidays();
    Ok(
        range_holidays.iter().map(|holiday|{date_chrono_to_py(py, *holiday)}).collect::<Vec<&PyDate>>()
    )
}

/// 休日曜日データの取得  
/// Return
/// - 休日曜日のset
#[pyfunction]
fn get_holiday_weekdays() -> Result<HashSet<u32>, Error>{
    let weekdays = rs_workdays::get_holiday_weekdays();
    Ok(
        weekdays.iter().map(|weekday|{
            weekday.num_days_from_monday()
        }).collect::<HashSet<u32>>()
    )
}

/// 営業時間境界の取得  
/// Return
/// - 営業時間境界のリスト
#[pyfunction]
fn get_intraday_borders<'p>(py: Python<'p>) -> Result<Vec<HashMap<String, &'p PyTime>>, Error>{
    let borders = rs_workdays::get_intraday_borders();
    Ok(
        borders.iter().map(|border|{
            let mut border_map: HashMap<String, &PyTime> = HashMap::new();
            border_map.insert("start".to_string(), time_chrono_to_py(py,border.start));
            border_map.insert("end".to_string(), time_chrono_to_py(py, border.end));
            border_map
        }).collect::<Vec<_>>()
    )
}

/// 内閣府のデータを指定したパスにソースとして保存
/// Argment
/// - source_path: 保存するcsvのパス
#[pyfunction]
fn make_source_naikaku(source_csv_path: String) -> Result<(), Error> {
    rs_workdays::make_source_naikaku(&source_csv_path)?;
    Ok(())
}

/// 内閣府による祝日データを取得して祝日に設定する(同期)(feature!="wasm")  
/// Argments  
/// - start_year=2016: 利用範囲の開始年
/// - end_year=2025: 利用範囲の終了年
#[pyfunction(start_year="2016", end_year="2025")]
fn request_holidays_naikaku(start_year: i32, end_year: i32) -> Result<(), Error> {
    rs_workdays::request_holidays_naikaku(start_year, end_year)?;
    Ok(())
}

/// start_dateからend_dateまでの営業日を取得  
/// Argments
/// - start_date: 開始日
/// - end_date: 終了日
/// - closed: 境界を含めるかどうか
///     - "left": 終了境界を含めない
///     - "right": 開始境界を含めない
///     - "not": どちらの境界も含める
///     - "both": どちらの境界も含めない
/// 
/// Return  
/// 営業日のリスト
#[pyfunction(closed="\"left\"")]
fn get_workdays<'p>(
    py: Python<'p>,
    start_date: &PyDate, 
    end_date: &PyDate, 
    closed: &str
) -> Result<Vec<&'p PyDate>, Error> {
    let start_date = date_py_to_chrono(start_date);
    let end_date = date_py_to_chrono(end_date);
    let closed = match closed {
        "left" => {rs_workdays::Closed::Left},
        "right" => {rs_workdays::Closed::Right},
        "both" => {rs_workdays::Closed::Both},
        "not" => {rs_workdays::Closed::Not},
        _ => {rs_workdays::Closed::Left}
    };

    let workdays = rs_workdays::get_workdays(start_date, end_date, closed);
    Ok(
        workdays.iter().map(|workday|{date_chrono_to_py(py, *workday)}).collect::<Vec<&PyDate>>()
    )
}

/// select_dateが営業日であるか判定  
/// Argment
/// - select_date: 指定する日
/// 
/// Return
/// 営業日であるかどうか
#[pyfunction]
fn check_workday(select_date: &PyDate) -> Result<bool, Error> {
    let select_date = date_py_to_chrono(select_date);
    Ok(rs_workdays::check_workday(select_date))
}

/// select_dateからdays分の次の営業日を取得  
/// Argments
/// - select_date: 指定する日
/// - days: 進める日数
/// 
/// Return  
/// one_day: 次の営業日
#[pyfunction(days="1")]
fn get_next_workday<'p>(
    py: Python<'p>,
    select_date: &PyDate, 
    days:i32
) -> Result<&'p PyDate, Error> {
    let select_date = date_py_to_chrono(select_date);
    let next_workday = rs_workdays::get_next_workday(select_date, days);
    Ok(date_chrono_to_py(py, next_workday))
}

/// select_dateからdays分の前の営業日を取得  
/// Argment
/// - select_date: 指定する日
/// - days: 減らす日数
/// 
/// Return  
/// one_day: 前の営業日
#[pyfunction(days="1")]
fn get_previous_workday<'p>(
    py: Python<'p>,
    select_date: &PyDate, 
    days: i32
) -> Result<&'p PyDate, Error> {
    let select_date = date_py_to_chrono(select_date);
    let previous_workday = rs_workdays::get_previous_workday(select_date, days);
    Ok(date_chrono_to_py(py, previous_workday))
}

/// 最近の営業日を取得  
/// Argments
/// - select_date: 指定する日
/// - is_after: 後の営業日を所得するかどうか
/// 
/// Return  
/// 最近の営業日
#[pyfunction(is_after="true")]
fn get_near_workday<'p>(
    py:Python<'p>,
    select_date: &PyDate, 
    is_after: bool
) -> Result<&'p PyDate, Error> {
    let select_date = date_py_to_chrono(select_date);
    let near_workday = rs_workdays::get_near_workday(select_date, is_after);
    Ok(date_chrono_to_py(py, near_workday))
}

/// start_dateからdays分だけの営業日のベクターを取得  
/// Argments
/// - start_date: 開始日
/// - days: 日数
/// 
/// Return  
/// workdays_vec: 営業日のベクター
#[pyfunction]
fn get_workdays_number<'p>(
    py: Python<'p>,
    start_date: &PyDate, 
    days: i32
) -> Result<Vec<&'p PyDate>, Error> {
    let start_date = date_py_to_chrono(start_date);
    let workdays = rs_workdays::get_workdays_number(start_date, days);
    Ok(
        workdays.iter().map(|workday|{date_chrono_to_py(py, *workday)}).collect::<Vec<&PyDate>>()
    )
}

/// select_datetimeが営業日・営業時間内であるかどうかを判定    
/// Argment
/// - select_datetime: 指定する日時
/// 
/// Return  
/// 営業日・営業時間内であるかどうか
#[pyfunction]
fn check_workday_intraday_naive(select_datetime: &PyDateTime) -> Result<bool, Error> {
    let select_date = datetime_py_to_chrono(select_datetime);
    Ok(rs_workdays::check_workday_intraday(select_date))
}

/// 次の営業日・営業時間内のdatetimeをその状態とともに取得  
/// Argment
/// - select_datetime: 指定する日時
/// 
/// Returns
/// - out_datetime: 次の営業日・営業時間内のdatetime
/// - 状態を示す文字列
///     - 'border_start': 営業時間の開始
///     - 'border_end': 営業時間の終了
#[pyfunction]
fn get_next_border_workday_intraday_naive<'p>(
    py: Python<'p>,
    select_datetime: &PyDateTime 
) -> Result<(&'p PyDateTime, String), Error> {
    let select_datetime = datetime_py_to_chrono(select_datetime);
    let (border_datetime, border_symbol) = rs_workdays::get_next_border_workday_intraday(select_datetime);
    Ok(
        (datetime_chrono_to_py(py, border_datetime), border_symbol.to_string())
    )
}

/// 前の営業日・営業時間内のdatetimeをその状態とともに取得  
/// Argment
/// - select_datetime: 指定する日時
/// - fore_is_end: 終了時間のときに次の終了時間を取得するかどうか
/// 
/// Returns
/// - out_datetime: 前の営業日・営業時間内のdatetime
/// - 状態を示す文字列
///     - 'border_start': 営業時間の開始
///     - 'border_end': 営業時間の終了
#[pyfunction(force_is_end="false")]
fn get_previous_border_workday_intraday_naive<'p>(
    py: Python<'p>,
    select_datetime: &PyDateTime,
    force_is_end: bool
) -> Result<(&'p PyDateTime, String), Error> {
    let select_datetime = datetime_py_to_chrono(select_datetime);
    let (border_datetime, border_symbol) = rs_workdays::get_previous_border_workday_intraday(
        select_datetime, 
        force_is_end
    );
    Ok(
        (datetime_chrono_to_py(py, border_datetime), border_symbol.to_string())
    )
}

/// 最近の営業日・営業時間内のdatetimeをその状態とともに取得．select_datetimeが営業日・営業時間内の場合そのまま返る．  
/// Argments
/// - select_datetime: 指定する日時
/// - is_after: 後ろを探索するかどうか
/// 
/// Returns
/// - out_datetime: 前の営業日・営業時間内のdatetime
/// - 状態を示す文字列
///     - 'border_intra': 営業時間内
///     - 'border_start': 営業時間の開始
///     - 'border_end': 営業時間の終了
#[pyfunction(is_after="true")]
fn get_near_workday_intraday_naive<'p>(
    py: Python<'p>,
    select_datetime: &PyDateTime,
    is_after: bool
) -> Result<(&'p PyDateTime, String), Error> {
    let select_datetime = datetime_py_to_chrono(select_datetime);
    let (border_datetime, border_symbol) = rs_workdays::get_near_workday_intraday(
        select_datetime, 
        is_after
    );
    Ok(
        (datetime_chrono_to_py(py, border_datetime), border_symbol.to_string())
    )
}

/// 営業日・営業時間を考慮しDateTimeを加算する．  
/// Argments
/// - select_datetime: 指定する日時
/// - dela_time: 加算するDuration
/// 
/// Return  
/// 加算された日時
#[pyfunction]
fn add_workday_intraday_datetime_naive<'p>(
    py: Python<'p>,
    select_datetime: &PyDateTime, 
    delta_time: &PyDelta
) -> Result<&'p PyDateTime, Error> {
    let select_datetime = datetime_py_to_chrono(select_datetime);
    let added_datetime = rs_workdays::add_workday_intraday_datetime(
        select_datetime, 
        duration_py_to_chrono(delta_time)
    );
    Ok(datetime_chrono_to_py(py, added_datetime))
}

/// start_datetimeからend_datetimeの営業日・営業時間を取得
/// Argments
/// - start_datetime: 開始日時
/// - end_datetime: 終了日時
/// 
/// Return
/// 営業日・営業時間のDuration
#[pyfunction]
fn get_timedelta_workdays_intraday_naive<'p>(
    py: Python<'p>,
    start_datetime: &PyDateTime,
    end_datetime: &PyDateTime
) -> Result<&'p PyDelta, Error> {
    let start_datetime = datetime_py_to_chrono( start_datetime);
    let end_datetime = datetime_py_to_chrono(end_datetime);
    let duration = rs_workdays::get_timedelta_workdays_intraday(start_datetime, end_datetime);
    Ok(duration_chrono_to_py(py, duration))
}


/// 営業日の取得，営業時間の演算，営業時間内データの抽出ができるライブラリ
#[pymodule]
fn py_workdays(py: Python, m: &PyModule) -> PyResult<()> {
    m.add("PyWorkdaysError", py.get_type::<PyWorkdaysError>())?;

    m.add_function(wrap_pyfunction!(set_holidays_csvs, m)?)?;
    m.add_function(wrap_pyfunction!(set_range_holidays, m)?)?;
    m.add_function(wrap_pyfunction!(add_range_holidays, m)?)?;
    m.add_function(wrap_pyfunction!(set_holiday_weekdays, m)?)?;
    m.add_function(wrap_pyfunction!(set_intraday_borders, m)?)?;
    m.add_function(wrap_pyfunction!(get_range_holidays, m)?)?;
    m.add_function(wrap_pyfunction!(get_holiday_weekdays, m)?)?;
    m.add_function(wrap_pyfunction!(get_intraday_borders, m)?)?;
    m.add_function(wrap_pyfunction!(make_source_naikaku, m)?)?;
    m.add_function(wrap_pyfunction!(request_holidays_naikaku, m)?)?;


    // workdays
    m.add_function(wrap_pyfunction!(get_workdays, m)?)?;
    m.add_function(wrap_pyfunction!(check_workday, m)?)?;
    m.add_function(wrap_pyfunction!(get_next_workday, m)?)?;
    m.add_function(wrap_pyfunction!(get_previous_workday, m)?)?;
    m.add_function(wrap_pyfunction!(get_near_workday, m)?)?;
    m.add_function(wrap_pyfunction!(get_workdays_number, m)?)?;

    // intraday
    m.add_function(wrap_pyfunction!(check_workday_intraday_naive, m)?)?;
    m.add_function(wrap_pyfunction!(get_next_border_workday_intraday_naive, m)?)?;
    m.add_function(wrap_pyfunction!(get_previous_border_workday_intraday_naive, m)?)?;
    m.add_function(wrap_pyfunction!(get_near_workday_intraday_naive, m)?)?;
    m.add_function(wrap_pyfunction!(add_workday_intraday_datetime_naive, m)?)?;
    m.add_function(wrap_pyfunction!(get_timedelta_workdays_intraday_naive, m)?)?;

    // extract
    /// np.datetime64のndarrayから営業日のものをboolとして抽出  
    /// Argment
    /// - datetime_64_numpy: 抽出したい日時のndarray
    /// 
    /// Return  
    /// ブールのndarray
    #[pyfn(m)]
    fn extract_workdays_bool_naive<'p>(
        py: Python<'p>, 
        int_64_numpy: PyReadonlyArray<i64,Ix1>
    ) -> PyResult<&'p PyArray<bool,Ix1>> {
        let int_64_numpy = int_64_numpy.as_array();
        let datetime_vec: Vec<NaiveDateTime> = int_64_numpy.iter().map(|x|{
            NaiveDateTime::from_timestamp(*x, 0)
        }).collect();
        let bool_vec = rs_workdays::extract_workdays_bool(&datetime_vec);
        let bool_array = Array::from_shape_vec(bool_vec.len(), bool_vec).unwrap();
        Ok(
            bool_array.into_pyarray(py)
        )
    } 

    /// np.datetime64のndarrayから営業時間のものをboolとして抽出
    /// Argment
    /// - datetime_vec: 抽出したい日時のndarray
    /// 
    /// Return  
    /// ブールのndarray
    #[pyfn(m)]
    fn extract_intraday_bool_naive<'p>(
        py: Python<'p>, 
        int_64_numpy:PyReadonlyArray<i64,Ix1>
    ) -> PyResult<&'p PyArray<bool,Ix1>> {
        let int_64_numpy = int_64_numpy.as_array();
        let datetime_vec: Vec<NaiveDateTime> = int_64_numpy.iter().map(|x|{
            NaiveDateTime::from_timestamp(*x, 0)
        }).collect();
        let bool_vec = rs_workdays::extract_intraday_bool(&datetime_vec);
        let bool_array = Array::from_shape_vec(bool_vec.len(), bool_vec).unwrap();
        Ok(
            bool_array.into_pyarray(py)
        )
    }

    /// np.datetime64のndarrayから営業日・営業時間のものをboolとして抽出
    /// Argment
    /// - datetime_vec: 抽出したい日時のndarray
    /// 
    /// Return
    /// ブールのndarray
    #[pyfn(m)]
    fn extract_workdays_intraday_bool_naive<'py>(
        py: Python<'py>, 
        int_64_numpy: PyReadonlyArray<i64,Ix1>
    ) -> PyResult<&'py PyArray<bool,Ix1>> {
        let int_64_numpy = int_64_numpy.as_array();
        let datetime_vec: Vec<NaiveDateTime> = int_64_numpy.iter().map(|x|{
            NaiveDateTime::from_timestamp(*x, 0)
        }).collect();
        let bool_vec = rs_workdays::extract_workdays_intraday_bool(&datetime_vec);
        let bool_array = Array::from_shape_vec(bool_vec.len(), bool_vec).unwrap();
        Ok(
            bool_array.into_pyarray(py)
        )
    }

    Ok(())
}