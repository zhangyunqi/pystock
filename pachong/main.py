import tushare as ts

pro = ts.pro_api()


# 设置token
def set_token():
    ts.set_token("8e3c6429eaa36d0e2b6346489f769d0d459d1f03588c3cc77fd79f58")


if __name__ == '__main__':
    data = pro.stock_basic(exchange='', list_status='L', fields='ts_code,symbol,name,area,industry,list_date')
    print(data)
