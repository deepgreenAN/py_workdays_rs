use chrono::{NaiveDate, Datelike, NaiveTime, NaiveDateTime, Timelike, Duration};
use pyo3::prelude::*;
use pyo3::types::{PyDate, PyDateAccess, PyDateTime, PyTime, PyTimeAccess, PyDelta, PyDeltaAccess};

pub fn date_py_to_chrono(py_date: &PyDate) -> NaiveDate {
    NaiveDate::from_ymd(
        py_date.get_year(),
        py_date.get_month() as u32,
        py_date.get_day() as u32
    )
}

pub fn date_chrono_to_py<'p>(py:Python<'p>, chrono_date: NaiveDate) -> &'p PyDate {
    PyDate::new(
        py,
        chrono_date.year(), 
        chrono_date.month() as u8, 
        chrono_date.day() as u8
    ).unwrap()
}

pub fn time_py_to_chrono(py_time: &PyTime) -> NaiveTime {
    NaiveTime::from_hms(
        py_time.get_hour() as u32,
        py_time.get_minute() as u32,
        py_time.get_second() as u32
    )
}

pub fn time_chrono_to_py<'p>(py: Python<'p>, chrono_time: NaiveTime) -> &'p PyTime {
    PyTime::new(
        py,
        chrono_time.hour() as u8, 
        chrono_time.minute() as u8, 
        chrono_time.second() as u8,
        0_u32,
        None
    ).unwrap()
}


pub fn datetime_py_to_chrono(py_datetime: &PyDateTime) -> NaiveDateTime {
    NaiveDateTime::new(
        NaiveDate::from_ymd(
            py_datetime.get_year(),
            py_datetime.get_month() as u32,
            py_datetime.get_day() as u32
        ),
        NaiveTime::from_hms(
            py_datetime.get_hour() as u32,
            py_datetime.get_minute() as u32,
            py_datetime.get_second() as u32
        )
    )
}

pub fn datetime_chrono_to_py<'p>(py: Python<'p>, chrono_datetime: NaiveDateTime) -> &'p PyDateTime {
    PyDateTime::new(
        py,
        chrono_datetime.year(),
        chrono_datetime.month() as u8,
        chrono_datetime.day() as u8,
        chrono_datetime.hour() as u8,
        chrono_datetime.minute() as u8,
        chrono_datetime.second() as u8,
        0_u32,
        None
    ).unwrap()
}

pub fn duration_py_to_chrono(py_delta: &PyDelta) -> Duration {
    Duration::days(py_delta.get_days() as i64) +
    Duration::seconds(py_delta.get_seconds() as i64)
}

pub fn duration_chrono_to_py<'p>(py: Python<'p>, duration: Duration) -> &PyDelta {
    let days = duration.num_days();
    let seconds = duration.num_seconds() - days * 24_i64 * 3600_i64;
    PyDelta::new(
        py,
        days as i32,
        seconds as i32,
        0_i32,
        true
    ).unwrap()
}