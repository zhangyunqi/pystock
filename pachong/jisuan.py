import pandas as pd
import pachong.main as mn


class JiSuan:
    OPERATORS = ['le', 'ge', 'lt', 'gt', 'eq', 'ne']
    ZHIBIAO = ['bollm', 'bollu', 'bolll', 'dif', 'dea', 'macd', 'rsi6', 'rsi12', 'rsi24', 'sma5', 'sma10', 'sma30',
               'sma60', 'sma20', 'kdjk', 'kdjd', 'kdjj', 'tor', 'chgamt', 'chg', 'close', 'high', 'low', 'open',
               'volume']

    @staticmethod
    def pre(df, current_row, index_name: str, n_days):
        """ 向前n天的某一股票指标
        :param df DataFrame数据
        :param current_row 当前处理股票信息的行号
        :param n_days 向前多少天
        :param index_name 获取指标的名称
        """
        return df.iloc[current_row - n_days][index_name:str]

    @staticmethod
    def after(df, current_row, index_name: str, n_days):
        """ 向后n天的某一股票指标
                :param df DataFrame数据
                :param current_row 当前处理股票信息的行号
                :param n_days 向后多少天
                :param index_name 获取指标的名称
                """
        return df.iloc[current_row + n_days][index_name]

    @staticmethod
    def current(df, current_row, index_name):
        return df.iloc[current_row][index_name]

    @staticmethod
    def index(df, current_row, index_name: str, n_days=0):
        """ 向前n天的某一股票指标
        :param df DataFrame数据
        :param current_row 当前处理股票信息的行号
        :param n_days 向前多少天
        :param index_name 获取指标的名称
        """
        return df.loc[current_row][index_name]

    @classmethod
    def jisuan(cls, stocks: list, gongshi: str, fq_flag: int = 2):
        # 解析公式
        gongshi: str = gongshi.replace("index(", "JiSuan.index(stock_infos,index,").replace(" ", "")
        for index in JiSuan.ZHIBIAO:
            if gongshi.__contains__(index + ",") | gongshi.__contains__(index + ")"):
                gongshi = gongshi.replace(index, "'" + index + "'")
        # 符合条件的
        stock_dict = {}
        for stock_code in stocks:
            # 符合条件的股票信息
            fit_stock_infos = []
            # 股票指标信息
            stock_infos = mn.calculate_zhibiao(stock_code, fq_flag)
            stock_infos.rename(columns={'boll': 'bollm', 'boll_ub': 'bollu', 'boll_lb': 'bolll',
                                        'macd': 'dif', 'macds': 'dea', 'macdh': 'macd',
                                        'rsi_6': 'rsi6', 'rsi_12': 'rsi12', 'rsi_24': 'rsi24',
                                        'close_5_sma': 'sma5', 'close_10_sma': 'sma10', 'close_30_sma': 'sma30',
                                        'close_60_sma': 'sma60', 'close_20_sma': 'sma20'}
                               , inplace=True)
            if len(stock_infos) < 100:
                continue
            for index, row in stock_infos.iterrows():
                if int(index) < 10:
                    continue
                if int(index) > len(stock_infos) - 10:
                    break
                if eval("" + gongshi):
                    fit_stock_infos.append(row)
            if len(fit_stock_infos) != 0:
                stock_dict[stock_code] = fit_stock_infos
        print(stock_dict)
        return stock_dict


if __name__ == '__main__':
    df = pd.read_csv("D:\\1111.csv", encoding="GBK")
    df.rename(columns={'boll': 'bollm', 'boll_ub': 'bollu', 'boll_lb': 'bolll',
                       'macd': 'dif', 'macds': 'dea', 'macdh': 'macd',
                       'rsi_6': 'rsi6', 'rsi_12': 'rsi12', 'rsi_24': 'rsi24',
                       'close_5_sma': 'sma5', 'close_10_sma': 'sma10', 'close_30_sma': 'sma30',
                       'close_60_sma': 'sma60', 'close_20_sma': 'sma20'}
              , inplace=True)
    gongshi: str = "(index(macd)<index(macd,-2)*1.5) & (index(kdjk)*1.2 >= index(kdjj,2))"
    gongshi: str = gongshi.replace("index(", "JiSuan.index(df,12,").replace(" ", "")

    for index in JiSuan.ZHIBIAO:
        if gongshi.__contains__(index + ",") | gongshi.__contains__(index + ")"):
            gongshi = gongshi.replace(index, "'" + index + "'")

    print(gongshi)
    print(eval("" + gongshi))
