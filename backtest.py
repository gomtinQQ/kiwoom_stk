# /usr/bin/python3
#-*- coding: utf-8 -*-
#Author : jaehyek Choi
# 목적 : zipline을 활용하여,  만들거나 만든 트레이딩 알고리즘을 검증한다.
# zipline은  https://github.com/jaehyek/zipline 처음에 설치방법에 대해
# 설명을 했다. Python 3.6 32bit 으로.
# 키움증권 OCX 가 32bit이므로 우리가 사용하는 환경은  32bit이다.
#---------------------------------------------------------

import pandas_datareader.data as web
import pandas as pd
import datetime
import matplotlib.pyplot as plt
from zipline.api import order_target, record, symbol
from zipline.algorithm import TradingAlgorithm

import pyalgo

def initialize(context):
    context.i = 0
    context.sym = symbol('AAPL')
    context.hold = False

def handle_data(context, data):
    context.i += 1
    if context.i < 20:
        return

    buy = False
    sell = False

    ma5 = data.history(context.sym, 'price', 5, '1d').mean()
    ma20 = data.history(context.sym, 'price', 20, '1d').mean()

    if ma5 > ma20 and context.hold == False:
        order_target(context.sym, 100)
        context.hold = True
        buy = True
    elif ma5 < ma20 and context.hold == True:
        order_target(context.sym, -100)
        context.hold = False
        sell = True

    record(AAPL=data.current(context.sym, "price"), ma5=ma5, ma20=ma20, buy=buy, sell=sell)

def temp():
    df = pyalgo.get_dataframe_with_code("005440")
    df = pyalgo.add_이동평균선_to_dataframe(df, [5, 20])

    serialdatetime = pd.Series([pd.to_datetime(bb, format="%Y%m%d") for bb in df.index])
    df2 = df.set_index(serialdatetime)
    data = df2[["현재가"]]
    data.columns = ['AAPL']
    print("data length :%s"%(len(data)))

    algo = TradingAlgorithm(initialize=initialize, handle_data=handle_data)
    result = algo.run(data)

    plt.plot(result.index, result.portfolio_value)
    plt.show()



def backtest():
    # data
    start = datetime.datetime(2010, 1, 1)
    end = datetime.datetime(2016, 3, 29)
    data = web.DataReader("AAPL", "yahoo", start, end)

    data = data[['Adj Close']]
    data.columns = ['AAPL']
    data = data.tz_localize('UTC')

    algo = TradingAlgorithm(initialize=initialize, handle_data=handle_data)
    result = algo.run(data)

    # plt.plot(result.index, result.portfolio_value)
    # plt.show()

    plt.plot(result.index, result.ma5)
    plt.plot(result.index, result.ma20)
    plt.legend(loc='best')

    plt.plot(result.ix[result.buy == True].index, result.ma5[result.buy == True], '^')
    plt.plot(result.ix[result.sell == True].index, result.ma5[result.sell == True], 'v')

    plt.show()



if __name__ == "__main__" :
    backtest()