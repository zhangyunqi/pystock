import math
import time

import requests
import tushare as ts
import pandas as pd
from pandas import DataFrame
from stockstats import StockDataFrame

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
        for n in range(0, math.ceil(len(stock_datas) / 3000)):
            end_date: str = stock_datas.iloc[n * 3000]["日期"]
            start_date: str = (
                stock_datas.iloc[len(stock_datas) - 1]["日期"] if (((n + 1) * 3000 - 1) >= len(stock_datas)) else
                stock_datas.iloc[(n + 1) * 3000 - 1]["日期"])
            df = pro.adj_factor(ts_code=stock_code, start_date=start_date.replace("-", ""),
                                end_date=end_date.replace("-", ""))
            if n == 0:
                all_data = df
            else:
                all_data = pd.concat([all_data, df], axis=0)

    all_data.to_csv(stock_factor_file_path.format(wangyi_stock_code), encoding="GBK")


# 提取所有股票的历史复权因子
def get_all_stock_factor():
    i = 1
    stocks: DataFrame = pd.read_csv(stock_list_path, encoding='GBK')
    for code in stocks['ts_code']:
        get_stock_factor(code)
        i = i + 1
        print(i)
        if 0 == (i % 100):
            print("暂停")
            # 每166次暂停一分钟，因为接口一分钟只能500次
            time.sleep(60)


# 计算前复权价格
def calculate_fqq(wangyi_stock_code: str):
    stock_datas = pd.read_csv(stock_file_path.format(wangyi_stock_code), encoding="GBK", index_col='日期')
    stock_factors = pd.read_csv(stock_factor_file_path.format(wangyi_stock_code), encoding="GBK",
                                index_col='trade_date')
    qfq = []
    hfq = []

    new_factor = stock_factors.iloc[0]['adj_factor']
    for row in stock_datas.itertuples():
        factor_index = int(str.replace(row.Index, '-', ''))
        factor = stock_factors.loc[factor_index]['adj_factor']
        factor = 1 if factor is None else factor
        # print(float(row.收盘价) * factor)
        hfq.append(float(row.收盘价) * factor)
        qfq.append(float(row.收盘价) * factor / new_factor)
    stock_datas['后复权'] = hfq
    stock_datas['前复权'] = qfq
    print(stock_datas)


# 计算指标
def calculate_zhibiao(wangyi_stock_code: str, fq_flag: int):
    # 股票数据
    stock_datas: pd.DataFrame = pd.read_csv(stock_file_path.format(wangyi_stock_code)
                                            , encoding="GBK")
    if fq_flag != 0:
        # 复权处理
        # 股票复权因子数据
        stock_factors: pd.DataFrame = pd.read_csv(stock_factor_file_path.format(wangyi_stock_code)
                                                  , encoding="GBK", index_col='trade_date')
        if fq_flag == 1:
            # 前复权
            # 最新的复权因子
            new_factor = stock_factors.iloc[0]['adj_factor']
            stock_datas["收盘价"] = list(
                map(lambda x, y: y * (stock_factors.loc[int(str.replace(x, '-', ''))]['adj_factor']) / new_factor,
                    stock_datas["日期"], stock_datas["收盘价"]))
            stock_datas["最高价"] = list(
                map(lambda x, y: y * (stock_factors.loc[int(str.replace(x, '-', ''))]['adj_factor']) / new_factor,
                    stock_datas["日期"], stock_datas["最高价"]))
            stock_datas["最低价"] = list(
                map(lambda x, y: y * (stock_factors.loc[int(str.replace(x, '-', ''))]['adj_factor']) / new_factor,
                    stock_datas["日期"], stock_datas["最低价"]))
            stock_datas["开盘价"] = list(
                map(lambda x, y: y * (stock_factors.loc[int(str.replace(x, '-', ''))]['adj_factor']) / new_factor,
                    stock_datas["日期"], stock_datas["开盘价"]))
            stock_datas["前收盘"] = list(
                map(lambda x, y: y * (stock_factors.loc[int(str.replace(x, '-', ''))]['adj_factor']) / new_factor,
                    stock_datas["日期"], stock_datas["前收盘"]))
        elif fq_flag == 2:
            # 后复权
            stock_datas["收盘价"] = list(
                map(lambda x, y: y * stock_factors.loc[int(str.replace(x, '-', ''))]['adj_factor'],
                    stock_datas["日期"], stock_datas["收盘价"]))
            stock_datas["最高价"] = list(
                map(lambda x, y: y * stock_factors.loc[int(str.replace(x, '-', ''))]['adj_factor'],
                    stock_datas["日期"], stock_datas["最高价"]))
            stock_datas["最低价"] = list(
                map(lambda x, y: y * stock_factors.loc[int(str.replace(x, '-', ''))]['adj_factor'],
                    stock_datas["日期"], stock_datas["最低价"]))
            stock_datas["开盘价"] = list(
                map(lambda x, y: y * stock_factors.loc[int(str.replace(x, '-', ''))]['adj_factor'],
                    stock_datas["日期"], stock_datas["开盘价"]))
            stock_datas["前收盘"] = list(
                map(lambda x, y: y * stock_factors.loc[int(str.replace(x, '-', ''))]['adj_factor'],
                    stock_datas["日期"], stock_datas["前收盘"]))

    # 过滤停牌的交易日，条件"收盘价","最高价","最低价","开盘价","成交量"均为0
    stock_datas = stock_datas[(stock_datas["收盘价"] != 0) & (stock_datas["最高价"] != 0)
                              & (stock_datas["最低价"] != 0) & (stock_datas["开盘价"] != 0)
                              & (stock_datas["成交量"] != 0)]
    # 修改列
    stock_datas.rename(
        columns={'日期': 'date', '收盘价': 'close', '最高价': 'high', '最低价': 'low', '开盘价': 'open', '成交量': 'volume',
                 '换手率': 'tor', '涨跌额': 'chgamt', '涨跌幅': 'chg'}, inplace=True)
    # 将数据倒序输出
    stock_datas = stock_datas.reindex(index=stock_datas.index[::-1])
    stock = StockDataFrame.retype(stock_datas)
    # sma
    stock['close_5_sma'], stock['close_10_sma'], stock['close_30_sma'], stock['close_60_sma']
    # ema
    # boll:boll-中线  boll_ub:boll-up上线  boll_lb: boll下线
    stock['boll'], stock['boll_ub'], stock['boll_lb']
    # macd:DIF macds:DEA macdh*2:MACD
    stock['macd'], stock['macds'], stock['macdh']
    # kdj
    stock['kdjk'], stock['kdjd'], stock['kdjj']
    # rsi
    stock['rsi_6'], stock['rsi_12'], stock['rsi_24']

    stock.reset_index(level=None, drop=False, inplace=True, col_level=0, col_fill='')

    return stock
