use pyo3::prelude::*;
use pyo3::wrap_pyfunction;
use numpy::{IntoPyArray, PyArray, PyReadonlyArray, Ix1};
use ndarray::{Array};

use chrono::{NaiveDate, NaiveDateTime, Duration};

pub mod global;
pub mod workdays;
pub mod intraday;
pub mod extract;

use global::{set_range_holidays};

use workdays::{get_workdays, check_workday, get_next_workday, get_previous_workday, get_near_workday};
use workdays::{get_workdays_number};
use intraday::{check_workday_intraday, get_next_border_workday_intraday, get_previous_border_workday_intraday, get_near_workday_intraday};
use intraday::{add_workday_intraday_datetime, sub_workday_intraday_datetime, get_timedelta_workdays_intraday};

use extract::{extract_workdays_bool_vec, extract_intraday_bool_vec, extract_workdays_intraday_bool_vec};

#[pyfunction]
fn set_range_holidays_rs(date_str_vec:Vec<String>, start_year:i32, end_year:i32) -> PyResult<()> {
    let date_vec: Vec<NaiveDate> = date_str_vec.iter().cloned()
    .map(|x|{NaiveDate::parse_from_str(&x, "%Y-%m-%d").unwrap()}).collect();
    set_range_holidays(date_vec, start_year, end_year);
    Ok(())
}


#[pyfunction]
fn get_workdays_rs(start_date_str:String, end_date_str:String, closed:String) -> PyResult<Vec<String>> {
    let start_date = NaiveDate::parse_from_str(&start_date_str, "%Y-%m-%d").unwrap();
    let end_date =  NaiveDate::parse_from_str(&end_date_str, "%Y-%m-%d").unwrap();
    let workdays: Vec<NaiveDate> = get_workdays(start_date, end_date, &closed);
    let workdays_str: Vec<String> = workdays.iter().cloned().map(|x|{x.format("%Y-%m-%d").to_string()}).collect();
    Ok(workdays_str)
}

#[pyfunction]
fn check_workday_rs(select_date_str:String) -> PyResult<bool> {
    let select_date = NaiveDate::parse_from_str(&select_date_str, "%Y-%m-%d").unwrap();
    Ok(check_workday(select_date))
}

#[pyfunction]
fn get_next_workday_rs(select_date_str:String, days:i32) -> PyResult<String> {
    let select_date = NaiveDate::parse_from_str(&select_date_str, "%Y-%m-%d").unwrap();
    let return_date = get_next_workday(select_date, days);
    Ok(return_date.format("%Y-%m-%d").to_string())
}

#[pyfunction]
fn get_previous_workday_rs(select_date_str:String, days:i32) -> PyResult<String> {
    let select_date = NaiveDate::parse_from_str(&select_date_str, "%Y-%m-%d").unwrap();
    let return_date = get_previous_workday(select_date, days);
    Ok(return_date.format("%Y-%m-%d").to_string())
}

#[pyfunction]
fn get_near_workday_rs(select_date_str:String, is_after:bool) -> PyResult<String> {
    let select_date = NaiveDate::parse_from_str(&select_date_str, "%Y-%m-%d").unwrap();
    let return_date = get_near_workday(select_date, is_after);
    Ok(return_date.format("%Y-%m-%d").to_string())
}

#[pyfunction]
fn get_workdays_number_rs(start_date_str:String, days:i32) -> PyResult<Vec<String>> {
    let start_date = NaiveDate::parse_from_str(&start_date_str, "%Y-%m-%d").unwrap();
    let workdays: Vec<NaiveDate> = get_workdays_number(start_date, days);
    let workdays_str: Vec<String> = workdays.iter().cloned().map(|x|{x.format("%Y-%m-%d").to_string()}).collect();
    Ok(workdays_str)
}

#[pyfunction]
fn check_workday_intraday_rs(select_datetime_str:String) -> PyResult<bool> {
    let select_datetime = NaiveDateTime::parse_from_str(&select_datetime_str, "%Y-%m-%d %H:%M:%S").unwrap();
    let return_bool: bool = check_workday_intraday(select_datetime);
    Ok(return_bool)
}

#[pyfunction]
fn get_next_border_workday_intraday_rs(select_datetime_str:String) -> PyResult<(String, String)> {
    let select_datetime = NaiveDateTime::parse_from_str(&select_datetime_str, "%Y-%m-%d %H:%M:%S").unwrap();
    let (return_datetime, return_symbol_str) = get_next_border_workday_intraday(select_datetime);
    let return_datetime_str = return_datetime.format("%Y-%m-%d %H:%M:%S").to_string();
    Ok((return_datetime_str, return_symbol_str.to_string()))
}

#[pyfunction]
fn get_previous_border_workday_intraday_rs(select_datetime_str:String, force_is_end:bool) -> PyResult<(String, String)> {
    let select_datetime = NaiveDateTime::parse_from_str(&select_datetime_str, "%Y-%m-%d %H:%M:%S").unwrap();
    let (return_datetime, return_symbol_str) = get_previous_border_workday_intraday(select_datetime, force_is_end);
    let return_datetime_str = return_datetime.format("%Y-%m-%d %H:%M:%S").to_string();
    Ok((return_datetime_str, return_symbol_str.to_string()))
}

#[pyfunction]
fn get_near_workday_intraday_rs(select_datetime_str:String, is_after:bool) -> PyResult<(String, String)> {
    let select_datetime = NaiveDateTime::parse_from_str(&select_datetime_str, "%Y-%m-%d %H:%M:%S").unwrap();
    let (return_datetime, return_symbol_str) = get_near_workday_intraday(select_datetime, is_after);
    let return_datetime_str = return_datetime.format("%Y-%m-%d %H:%M:%S").to_string();
    Ok((return_datetime_str, return_symbol_str.to_string()))
}

#[pyfunction]
fn add_workday_intraday_datetime_rs(select_datetime_str:String, delta_time_sec:i64) -> PyResult<String> {
    let select_datetime = NaiveDateTime::parse_from_str(&select_datetime_str, "%Y-%m-%d %H:%M:%S").unwrap();
    let duration = Duration::seconds(delta_time_sec); 
    let return_datetime = add_workday_intraday_datetime(select_datetime, duration);
    let return_datetime_str = return_datetime.format("%Y-%m-%d %H:%M:%S").to_string();
    Ok(return_datetime_str)
}

#[pyfunction]
fn sub_workday_intraday_datetime_rs(select_datetime_str:String, delta_time_sec:i64) -> PyResult<String> {
    let select_datetime = NaiveDateTime::parse_from_str(&select_datetime_str, "%Y-%m-%d %H:%M:%S").unwrap();
    let duration = Duration::seconds(delta_time_sec); 
    let return_datetime = sub_workday_intraday_datetime(select_datetime, duration);
    let return_datetime_str = return_datetime.format("%Y-%m-%d %H:%M:%S").to_string();
    Ok(return_datetime_str)
}

#[pyfunction]
fn get_timedelta_workdays_intraday_rs(start_datetime_str:String, end_datetime_str:String) -> PyResult<i64> {
    let start_datetime =  NaiveDateTime::parse_from_str(&start_datetime_str, "%Y-%m-%d %H:%M:%S").unwrap();
    let end_datetime = NaiveDateTime::parse_from_str(&end_datetime_str, "%Y-%m-%d %H:%M:%S").unwrap();
    let return_duration = get_timedelta_workdays_intraday(start_datetime, end_datetime);
    let return_sec = return_duration.num_seconds();
    Ok(return_sec)
}


#[pymodule]
fn rs_workdays(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_wrapped(wrap_pyfunction!( set_range_holidays_rs ))?;

    // workdays
    m.add_wrapped(wrap_pyfunction!( get_workdays_rs ))?;
    m.add_wrapped(wrap_pyfunction!( check_workday_rs ))?;
    m.add_wrapped(wrap_pyfunction!( get_next_workday_rs ))?;
    m.add_wrapped(wrap_pyfunction!( get_previous_workday_rs ))?;
    m.add_wrapped(wrap_pyfunction!( get_near_workday_rs))?;
    m.add_wrapped(wrap_pyfunction!( get_workdays_number_rs))?;

    // intraday
    m.add_wrapped(wrap_pyfunction!( check_workday_intraday_rs ))?;
    m.add_wrapped(wrap_pyfunction!( get_next_border_workday_intraday_rs ))?;
    m.add_wrapped(wrap_pyfunction!( get_previous_border_workday_intraday_rs ))?;
    m.add_wrapped(wrap_pyfunction!( get_near_workday_intraday_rs ))?;
    m.add_wrapped(wrap_pyfunction!( add_workday_intraday_datetime_rs ))?;
    m.add_wrapped(wrap_pyfunction!( sub_workday_intraday_datetime_rs ))?;
    m.add_wrapped(wrap_pyfunction!( get_timedelta_workdays_intraday_rs ))?;

    // extract
    #[pyfn(m, "extract_workdays_bool_numpy_rs")]
    fn extract_workdays_bool_numpy_rs<'py>(py: Python<'py>, datetime_64_numpy:PyReadonlyArray<i64,Ix1>) 
    -> &'py PyArray<bool,Ix1> {
        let datetime_64_numpy = datetime_64_numpy.as_array();
        let datetime_vec: Vec<NaiveDateTime> = datetime_64_numpy.iter().map(|x|{NaiveDateTime::from_timestamp(*x, 0)}).collect();
        let bool_vec = extract_workdays_bool_vec(&datetime_vec);
        let bool_array = Array::from_shape_vec(bool_vec.len(), bool_vec).unwrap();
        bool_array.into_pyarray(py)
    } 

    #[pyfn(m, "extract_intraday_bool_numpy_rs")]
    fn extract_intraday_bool_numpy_rs<'py>(py: Python<'py>, datetime_64_numpy:PyReadonlyArray<i64,Ix1>)
    -> &'py PyArray<bool,Ix1> {
        let datetime_64_numpy = datetime_64_numpy.as_array();
        let datetime_vec: Vec<NaiveDateTime> = datetime_64_numpy.iter().map(|x|{NaiveDateTime::from_timestamp(*x, 0)}).collect();
        let bool_vec = extract_intraday_bool_vec(&datetime_vec);
        let bool_array = Array::from_shape_vec(bool_vec.len(), bool_vec).unwrap();
        bool_array.into_pyarray(py)
    }

    #[pyfn(m, "extract_workdays_intraday_bool_numpy_rs")]
    fn extract_workdays_intraday_bool_numpy_rs<'py>(py: Python<'py>, datetime_64_numpy:PyReadonlyArray<i64,Ix1>)
    -> &'py PyArray<bool,Ix1> {
        let datetime_64_numpy = datetime_64_numpy.as_array();
        let datetime_vec: Vec<NaiveDateTime> = datetime_64_numpy.iter().map(|x|{NaiveDateTime::from_timestamp(*x, 0)}).collect();
        let bool_vec = extract_workdays_intraday_bool_vec(&datetime_vec);
        let bool_array = Array::from_shape_vec(bool_vec.len(), bool_vec).unwrap();
        bool_array.into_pyarray(py)
    }

    Ok(())
}