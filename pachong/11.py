import requests
import pandas as pd
# 网易地址获取股票历史信息地址
# http://quotes.money.163.com/service/chddata.html?code=1000001&start=19910403&end=20210823&fields=TCLOSE;HIGH;LOW;TOPEN;LCLOSE;CHG;PCHG;TURNOVER;VOTURNOVER;VATURNOVER;TCAP;MCAP

stock_file_path: str = "../data/stock/";

wangyi_stock_url: str = "http://quotes.money.163.com/service/chddata.html?" \
                        "code={}&start={}&end={}" \
                        "&fields=TCLOSE;HIGH;LOW;TOPEN;LCLOSE;CHG;PCHG;TURNOVER;VOTURNOVER;VATURNOVER;TCAP;MCAP"


def get_stock_history(stock_code: str, start_date: str, end_date: str, file_name=None, down_res=None):
    url = wangyi_stock_url.format(stock_code, start_date, end_date)
    data = requests.get(url)
    with open(stock_file_path+stock_code+".csv", "wb") as stream:
        stream.write(data.content)

