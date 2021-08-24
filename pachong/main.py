import requests
import tushare as ts
import pandas as pd
from pandas import DataFrame

# 设置tushare的token
ts.set_token("8e3c6429eaa36d0e2b6346489f769d0d459d1f03588c3cc77fd79f58")
# tushare主方法
pro = ts.pro_api()

csv_encoding = 'GBK'
filepath: str = "../data/"
stock_file_path: str = "../data/stock/"
stock_list_path: str = filepath + "stocklist.csv"
# 网易地址获取股票历史信息地址
# http://quotes.money.163.com/service/chddata.html?code=1000001&start=19910403&end=20210823&fields=TCLOSE;HIGH;LOW;TOPEN;LCLOSE;CHG;PCHG;TURNOVER;VOTURNOVER;VATURNOVER;TCAP;MCAP
wangyi_stock_url: str = "http://quotes.money.163.com/service/chddata.html?" \
                        "code={}&start={}&end={}" \
                        "&fields=TCLOSE;HIGH;LOW;TOPEN;LCLOSE;CHG;PCHG;TURNOVER;VOTURNOVER;VATURNOVER;TCAP;MCAP"


# 获取所有的股票
def get_stock_all():
    data: DataFrame = pro.stock_basic(exchange='', list_status='L',
                                      fields='ts_code, symbol, name, area, industry, fullname,'
                                             ' enname, cnspell, market, exchange, curr_type,'
                                             ' list_status, list_date, delist_date, is_hs')
    data.to_csv(stock_list_path, encoding=csv_encoding, index=False)


# 获取所有的股票历史数据

def get_all_stocks_history():
    print(1)


# 获取单个股票历史数据
def get_stock_history(stock_code: str, start_date: str, end_date: str, file_name=None, down_res=None):
    url = wangyi_stock_url.format(stock_code, start_date, end_date)
    data = requests.get(url)
    with open(stock_file_path + stock_code + ".csv", "wb") as stream:
        stream.write(data.content)
