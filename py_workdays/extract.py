import datetime
import numpy as np
import pandas as pd
import datetime
from typing import Union, NoReturn

#import sys
#sys.path.append("py_workdays/rs_workdays/target/release")

from rs_workdays import extract_workdays_bool_numpy_rs, extract_intraday_bool_numpy_rs
from rs_workdays import extract_workdays_intraday_bool_numpy_rs
#from .option import option

# typehint
InputPandas = Union[pd.DataFrame, pd.Series]
OutputExtract = Union[np.ndarray, pd.DatetimeIndex, pd.DataFrame, pd.Series]

def extract_workdays_index(dt_index: pd.DatetimeIndex, return_as: str="index") -> Union[pd.DatetimeIndex, np.ndarray, NoReturn]:
    """
    pd.DatetimeIndexから，営業日のデータのものを抽出
    dt_index: pd.DatetimeIndex
        入力するDatetimeIndex，すでにdatetimeでソートしていることが前提
    return_as: str
        出力データの形式
        - "index": 引数としたdfの対応するインデックスを返す
        - "bool": 引数としたdfに対応するboolインデックスを返す
    """
    
    # 返り値の形式の指定
    return_as_set = {"index", "bool"}
    if not return_as in return_as_set:
        raise Exception("return_as must be any in {}".format(return_as_set))
        
    tz_dt = dt_index.tzinfo 
        
    if tz_dt is not None:
        naive_dt_index = dt_index.copy()
        naive_dt_index = naive_dt_index.tz_localize(None)  # 同じdatetimeの値をもつutc(python の localと挙動がことなることに注意)
    else:
        naive_dt_index = dt_index
        
    dt_value_datetime_64 = (naive_dt_index.values.astype(np.int64)/1.e9).astype(np.int64)
    extracted_bool = extract_workdays_bool_numpy_rs(dt_value_datetime_64)
    
    if return_as=="bool":
        return extracted_bool
    elif return_as=="index":
        extracted_dt_index = dt_index[extracted_bool]
        return extracted_dt_index
    else: # これは呼ばれない
        raise Exception("invalid return_as.")



def extract_workdays(df: InputPandas, return_as: str="df") -> OutputExtract:
    """
    データフレームから，営業日のデータのものを抽出．出力データ形式をreturn_asで指定する．
    df: pd.DataFrame(インデックスとしてpd.DatetimeIndex)
        入力データ
    return_as: str
        出力データの形式
        - "df": 抽出した新しいpd.DataFrameを返す
        - "index": 引数としたdfの対応するインデックスを返す
        - "bool": 引数としたdfに対応するboolインデックスを返す
    """
    
    # 返り値の形式の指定
    return_as_set = {"df", "index", "bool"}
    if not return_as in return_as_set:
        raise Exception("return_as must be any in {}".format(return_as_set))
    
    if return_as=="bool":
        workdays_bool_array = extract_workdays_index(df.index, return_as="bool")
        return workdays_bool_array
    elif return_as=="index":
        workdays_bool_array = extract_workdays_index(df.index, return_as="bool")
        workdays_df_indice = df.index[workdays_bool_array]
        return workdays_df_indice
    else:
        workdays_bool_array = extract_workdays_index(df.index, return_as="bool")
        out_df = df[workdays_bool_array].copy()
        return out_df


def extract_intraday_index(dt_index: pd.DatetimeIndex, return_as: str="index") -> Union[np.ndarray, pd.DatetimeIndex, NoReturn]:
    """
    pd.DatetimeIndexから，日中のデータのものを抽出．出力データ形式をreturn_asで指定する．
    dt_index: pd.DatetimeIndex
        入力するDatetimeIndex
    return_as: str
        出力データの形式
        - "index": 引数としたdfの対応するインデックスを返す
        - "bool": 引数としたdfに対応するboolインデックスを返す
    """
    
    # 返り値の形式の指定
    return_as_set = {"index", "bool"}
    if not return_as in return_as_set:
        raise Exception("return_as must be any in {}".format(return_as_set))
        
    tz_dt = dt_index.tzinfo 
        
    if tz_dt is not None:
        naive_dt_index = dt_index.copy()
        naive_dt_index = naive_dt_index.tz_localize(None)  # 同じdatetimeの値をもつutc(python の localと挙動がことなることに注意)
    else:
        naive_dt_index = dt_index
        
    dt_value_datetime_64 = (naive_dt_index.values.astype(np.int64)/1.e9).astype(np.int64)
    extracted_bool = extract_intraday_bool_numpy_rs(dt_value_datetime_64)
    
    if return_as=="bool":
        return extracted_bool
    elif return_as=="index":
        extracted_dt_index = dt_index[extracted_bool]
        return extracted_dt_index
    else: # これは呼ばれない
        raise Exception("invalid return_as.")


def extract_intraday(df: InputPandas, return_as: str="df") -> OutputExtract:
    """
    データフレームから，日中のデータのものを抽出．出力データ形式をreturn_asで指定する．
    df: pd.DataFrame(インデックスとしてpd.DatetimeIndex)
        入力データ
    return_as: str
        出力データの形式
        - "df": 抽出した新しいpd.DataFrameを返す
        - "index": 引数としたdfの対応するインデックスを返す
        - "bool": 引数としたdfに対応するboolインデックスを返す
    """
    
    # 返り値の形式の指定
    return_as_set = {"df", "index", "bool"}
    if not return_as in return_as_set:
        raise Exception("return_as must be any in {}".format(return_as_set))    

    if return_as=="bool":
        intraday_bool_array = extract_intraday_index(df.index, return_as="bool")
        return intraday_bool_array 
    elif return_as=="index":
        intraday_bool_array = extract_intraday_index(df.index, return_as="bool")
        intraday_indice = df.index[intraday_bool_array]
        return intraday_indice
    else:
        intraday_bool_array = extract_intraday_index(df.index, return_as="bool")
        out_df = df[intraday_bool_array].copy()
        return out_df


def extract_workdays_intraday_index(dt_index: pd.DatetimeIndex, return_as: str="index") -> Union[pd.DatetimeIndex, np.ndarray, NoReturn]:
    """
    pd.DatetimeIndexから，営業日+日中のデータのものを抽出．出力データ形式をreturn_asで指定する．
    dt_index: pd.DatetimeIndex
        入力するDatetimeIndex
    return_as: str
        出力データの形式
        - "index": 引数としたdfの対応するインデックスを返す
        - "bool": 引数としたdfに対応するboolインデックスを返す
    """
    
    # 返り値の形式の指定
    return_as_set = {"index", "bool"}
    if not return_as in return_as_set:
        raise Exception("return_as must be any in {}".format(return_as_set))
        
    tz_dt = dt_index.tzinfo 
        
    if tz_dt is not None:
        naive_dt_index = dt_index.copy()
        naive_dt_index = naive_dt_index.tz_localize(None)  # 同じdatetimeの値をもつutc(python の localと挙動がことなることに注意)
    else:
        naive_dt_index = dt_index
        
    dt_value_datetime_64 = (naive_dt_index.values.astype(np.int64)/1.e9).astype(np.int64)
    extracted_bool = extract_workdays_intraday_bool_numpy_rs(dt_value_datetime_64)
    
    if return_as=="bool":
        return extracted_bool
    elif return_as=="index":
        extracted_dt_index = dt_index[extracted_bool]
        return extracted_dt_index
    else: # これは呼ばれない
        raise Exception("invalid return_as.")


def extract_workdays_intraday(df: InputPandas, return_as: str="df") -> OutputExtract:
    """
    データフレームから，営業日+日中のデータのものを抽出．出力データ形式をreturn_asで指定する．
    df: pd.DataFrame(インデックスとしてpd.DatetimeIndex)
        入力データ
    return_as: str
        出力データの形式
        - "df": 抽出した新しいpd.DataFrameを返す
        - "index": 引数としたdfの対応するインデックスを返す
        - "bool": 引数としたdfに対応するboolインデックスを返す
    """
    
    # 返り値の形式の指定
    return_as_set = {"df", "index", "bool"}
    if not return_as in return_as_set:
        raise Exception("return_as must be any in {}".format(return_as_set))    
       
    if return_as=="bool":
        workday_intraday_bool_array = extract_workdays_intraday_index(df.index, return_as="bool")
        return workday_intraday_bool_array
    elif return_as=="index":
        workday_intraday_bool_array = extract_workdays_intraday_index(df.index, return_as="bool")
        workday_intraday_indice = df.index[workday_intraday_bool_array]
        return workday_intraday_indice
    else:
        workday_intraday_bool_array = extract_workdays_intraday_index(df.index, return_as="bool")
        out_df = df[workday_intraday_bool_array].copy()
        return out_df

    
if __name__ == "__main__":
    pass