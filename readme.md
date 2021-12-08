# 営業日・営業時間のデータを取得・抽出
営業日のデータを取得，pandas.DataFrameから営業日・営業時間のデータを抽出できる．計算にrustを用いており[高速](https://github.com/deepgreenAN/py_workdays_rs/wiki/%E9%80%9F%E5%BA%A6%E3%82%92%E8%A8%88%E6%B8%AC)．[こちら](https://github.com/deepgreenAN/py_workdays)のrust実装バージョン．

## installation
```
git clone https://github.com/deepgreenAN/py_workdays_rs.git
poetry install
poetry run maturin develop --release
poetry build
```

これでwhlファイルが作成される．

## 使い方

```python
import datetime
from pytz import timezone
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

import py_workdays
```

## 指定期間の営業日を取得


```python
start_date = datetime.date(2021,1,1)
end_date = datetime.date(2021,2,1)

workdays = py_workdays.get_workdays(start_date, end_date)
print(workdays)
```

    [datetime.date(2021, 1, 4), datetime.date(2021, 1, 5), datetime.date(2021, 1, 6), datetime.date(2021, 1, 7), datetime.date(2021, 1, 8), datetime.date(2021, 1, 12), datetime.date(2021, 1, 13), datetime.date(2021, 1, 14), datetime.date(2021, 1, 15), datetime.date(2021, 1, 18), datetime.date(2021, 1, 19), datetime.date(2021, 1, 20), datetime.date(2021, 1, 21), datetime.date(2021, 1, 22), datetime.date(2021, 1, 25), datetime.date(2021, 1, 26), datetime.date(2021, 1, 27), datetime.date(2021, 1, 28), datetime.date(2021, 1, 29)]
    

## 営業日かどうか判定


```python
select_date = datetime.date(2021,1,1)
py_workdays.check_workday(select_date)
```




    False



## 次の営業日を取得


```python
select_date = datetime.date(2021,1,1)

next_workday = py_workdays.get_next_workday(select_date, days=6)
next_workday
```




    datetime.date(2021, 1, 12)



## 指定する日数分の営業日を取得


```python
start_date = datetime.date(2021,1,1)
days = 19

workdays = py_workdays.get_workdays_number(start_date, days)
print(workdays)
```

    [datetime.date(2021, 1, 4), datetime.date(2021, 1, 5), datetime.date(2021, 1, 6), datetime.date(2021, 1, 7), datetime.date(2021, 1, 8), datetime.date(2021, 1, 12), datetime.date(2021, 1, 13), datetime.date(2021, 1, 14), datetime.date(2021, 1, 15), datetime.date(2021, 1, 18), datetime.date(2021, 1, 19), datetime.date(2021, 1, 20), datetime.date(2021, 1, 21), datetime.date(2021, 1, 22), datetime.date(2021, 1, 25), datetime.date(2021, 1, 26), datetime.date(2021, 1, 27), datetime.date(2021, 1, 28), datetime.date(2021, 1, 29)]
    

## 営業日・営業時間内か判定

デフォルトでは，東京証券取引所の営業日(土日・祝日，振替休日を除く)・営業時間(9時～11時30分，12時30分～15時)として利用できる．


```python
select_datetime = datetime.datetime(2021,1,4,10,0,0)

py_workdays.check_workday_intraday(select_datetime)
```




    True



## 指定日時から最も近い次の営業日・営業時間の日時を取得


```python
select_datetime = datetime.datetime(2021,1,1,0,0,0)

next_border_datetime, border_symbol = py_workdays.get_next_border_workday_intraday(select_datetime)
next_border_datetime, border_symbol
```




    (datetime.datetime(2021, 1, 4, 9, 0), 'border_start')



## 指定日時とtimedeltaから営業時間分加算する


```python
select_datetime = datetime.datetime(2021,1,1,0,0,0)

added_datetime = py_workdays.add_workday_intraday_datetime(select_datetime, datetime.timedelta(hours=2))
added_datetime
```




    datetime.datetime(2021, 1, 4, 11, 0)



## 指定期間の営業時間分のtimedeltaを取得する


```python
jst = timezone("Asia/Tokyo")

start_datetime = jst.localize(datetime.datetime(2021,1,1,0,0,0))
end_datetime = jst.localize(datetime.datetime(2021,1,4,15,0,0))

workdays_intraday_timedelta = py_workdays.get_timedelta_workdays_intraday(start_datetime, end_datetime)
workdays_intraday_timedelta
```




    datetime.timedelta(seconds=18000)



## pandas.DataFrameから営業時間内のデータを抽出


```python
aware_df = pd.read_csv("aware_stock_df.csv", parse_dates=True, index_col="timestamp")
```


```python
y = aware_df.loc[:, "Open_6502"].values
x = np.arange(0, len(y))

plt.plot(x, y)
```




    [<matplotlib.lines.Line2D at 0x232c8af5160>]




    
<img src="https://dl.dropboxusercontent.com/s/1ktk51hehbwjqu4/output_27_1.png?dl=0">
    



```python
extracted = py_workdays.extract_workdays_intraday_bool(aware_df.index)
y = aware_df.loc[extracted, "Open_6502"]
x = np.arange(0, len(y))
plt.plot(x, y)
```




    [<matplotlib.lines.Line2D at 0x232c845c7c0>]




   <img src="https://dl.dropboxusercontent.com/s/v70h9rdvwrtpyo3/output_28_1.png?dl=0"> 

    


##  営業時間・休日データの設定 

休日とする曜日を整数で指定できる．デフォルトは土日(5,6)．営業時間は東京証券取引所のものであり，開始時間と終了時間のペアを複数指定できる


```python
config = py_workdays.config
print(config.holiday_weekdays)
print(config.intraday_borders)
```

    [5, 6]
    [{'start': datetime.time(9, 0), 'end': datetime.time(11, 30)}, {'start': datetime.time(12, 30), 'end': datetime.time(15, 0)}]
    

初めてのimport時に[内閣府のcsvファイル](https://www8.cao.go.jp/chosei/shukujitsu/syukujitsu.csv)を読み込んでパッケージ内部に保存する．デフォルトでは現在年の5年前から2年後までの祝日を利用できる．


```python
print(config.holiday_start_year)
print(config.holiday_end_year)
```

    2016
    2023
    

設定値は代入するか，リストの場合は`append`することで変更される


```python
config.intraday_borders = [{"start": datetime.time(9, 0), "end": datetime.time(13, 0)}]
print(config.intraday_borders)
```

    [{'start': datetime.time(9, 0), 'end': datetime.time(13, 0)}]
    

`add_range_holidays`で祝日の追加ができる


```python
config.add_range_holidays([datetime.date(2022, 12, 31)])
print(config.range_holidays[-1])
```

    2022-12-31
    

読み込むcsvを追加する場合は，`csv_source_paths`に`append`する．


```python
from pathlib import Path
some_csv_path = Path("some_csv.csv")
config.csv_source_paths.append(some_csv_path)
```

`some_source.csv`は以下のような形式になっている必要がある


```
1955-01-01,元日
1955-01-15,成人の日
1955-03-21,春分の日
```
