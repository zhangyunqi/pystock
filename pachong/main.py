import math
from datetime import datetime

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
stock_file_path: str = filepath + "stock/{}.csv"
stock_factor_file_path: str = filepath + "factor/{}.csv"
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


# 将tushare的股票代码转换成网易的股票代码
def convert_tushare_code_to_wangyi_code(tushare_code: str) -> str:
    exchange = tushare_code[7:9]
    if exchange == 'SH':
        return '0' + tushare_code[0:6]
    elif exchange == 'SZ':
        return '1' + tushare_code[0:6]


# 获取所有的股票历史数据 tushare和网易交易所对应 SZ:1 SH:0
def get_all_stocks_history():
    stocks: DataFrame = pd.read_csv(stock_list_path, encoding='GBK')
    for code in stocks['ts_code']:
        get_stock_history(convert_tushare_code_to_wangyi_code(code), '19890101', '20210824')


# 获取单个股票历史数据 stock_code:网易的数据 1000001
def get_stock_history(stock_code: str, start_date: str, end_date: str):
    url = wangyi_stock_url.format(stock_code, start_date, end_date)
    data = requests.get(url)
    with open(stock_file_path.format(stock_code), "wb") as stream:
        stream.write(data.content)


# 提取股票的历史复权因子, stock_code:tushare的股票code 000001.SZ
def get_stock_factor(stock_code: str) -> DataFrame:
    all_data: DataFrame
    wangyi_stock_code = convert_tushare_code_to_wangyi_code(stock_code)
    # 检查股票是否超过5000条，tushare只支持一次返回5000条
    stock_datas = pd.read_csv(stock_file_path.format(wangyi_stock_code), encoding="GBK")
    if len(stock_datas) <= 3000:
        df = pro.adj_factor(ts_code=stock_code, trade_date='')
        all_data = df
    else:
        for n in range(0, math.ceil(3000)):
            start_date = stock_datas[n * 3000]
            end_date = (stock_datas[len(stock_datas)]["日期"] if (((n + 1) * 3000 - 1) > len(stock_datas)) else
                        stock_datas[(n + 1) * 3000 - 1]["日期"])
            df = pro.adj_factor(ts_code=stock_code, start_date=datetime.strftime(start_date, '%Y%m%d'),
                                end_date=datetime.strftime(end_date, '%Y%m%d'))
            all_data = pd.concat([all_data, df], axis=0)

    all_data.to_csv(stock_factor_file_path.format(wangyi_stock_code), encoding="GBK")
