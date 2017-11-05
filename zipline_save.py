# /usr/bin/python3
#-*- coding: utf-8 -*-
#Author : jaehyek Choi
# 목적 : zipline을 활용하여,  만들거나 만든 트레이딩 알고리즘을 검증한다.
# zipline은  https://github.com/jaehyek/zipline 처음에 설치방법에 대해
# 설명을 했다. Python 3.6 32bit 으로.
# 키움증권 OCX 가 32bit이므로 우리가 사용하는 환경은  32bit이다.
#---------------------------------------------------------
# 중요 : 일단 zipline은 사용하지 않기로 당분간 결정.
# 이유1 는  value is not in [index] 이란 error가 계속 나오고 있어서.
# 이유2 는  zipline보다 backtrader가 더 사용하기 편하고, plot가 더 잘 나온다.
# 이유3 는  zipline이 python 3.6을 미지원과  pandas=0.18(최신=0.20)을 사용해야 하므로
# 결국 사용은 보류한다.

import pandas_datareader.data as web
import pandas as pd
from datetime import datetime as dt
import datetime
import matplotlib.pyplot as plt
from zipline.api import order_target, record, symbol, set_commission
from zipline.finance import commission
from zipline.algorithm import TradingAlgorithm
from zipline.utils.run_algo import run_algorithm
import pytz

import pyalgo

def initialize(context):
    context.i = 0
    context.sym = symbol('종가')
    context.hold = False
    set_commission(commission.PerDollar(cost=0.00165))

def handle_data(context, data):
    context.i += 1
    if context.i < 20:
        return

    buy = False
    sell = False

    ma5 = data.history(context.sym, 'price', bar_count=5, frequency='1d').mean()
    ma20 = data.history(context.sym, 'price', bar_count=20, frequency='1d').mean()

    if ma5 > ma20 and context.hold == False:
        order_target(context.sym, 100)
        context.hold = True
        buy = True
    elif ma5 < ma20 and context.hold == True:
        order_target(context.sym, -100)
        context.hold = False
        sell = True

    record(종가=data.current(context.sym, "price"), ma5=ma5, ma20=ma20, buy=buy, sell=sell)

def backtest():
    df = pyalgo.get_dataframe_with_code("005440")
    # df = pyalgo.add_이동평균선_to_dataframe(df, [5, 20])

    # df은 오름차순으로 되어 있다.

    # serialdatetime = [pd.to_datetime(bb, utc="UTC", format="%Y%m%d") for bb in df.index]
    serialdatetime = [dt.strptime(str(bb), "%Y%m%d") for bb in df.index]

    # dtstart = serialdatetime[0].astimezone(pytz.utc)
    # dtend = serialdatetime[-1].astimezone(pytz.utc)

    # dtstart = serialdatetime[0]
    # dtend = serialdatetime[-1]

    # dtstart = dt(2001, 1, 2, 0, 0, 0, 0, pytz.utc)
    # dtend = dt(2017, 9, 29, 0, 0, 0, 0, pytz.utc)

    start = str(df.index[0]) + "%s"
    dtstart = dt.strptime(start % ("000000"), "%Y%m%d%H%M%S").astimezone(pytz.utc)

    end = str(df.index[-1]) + "%s"
    dtend = dt.strptime(end % ("000000"), "%Y%m%d%H%M%S").astimezone(pytz.utc)

    # dtstart = dt(2001, 1, 2)
    # dtend = dt(2017, 9, 29 )
    #
    # indexnew = pd.date_range('2001/1/2', periods=4119)
    # indexnew = indexnew.tz_localize(None)


    df = df.set_index(pd.DatetimeIndex(serialdatetime))
    data = df[["현재가"]]
    data.columns = ['종가']
    # data = data.tz_localize(pytz.utc)

    print("data length :%s"%(len(data)))

    dfresult = run_algorithm(dtstart, dtend, initialize, 100000000.0, handle_data, data_frequency = 'daily', data=data)
    #
    # algo = TradingAlgorithm(initialize=initialize, handle_data=handle_data)
    # dfresult = algo.run(data)

    plt.plot(dfresult.index, dfresult.portfolio_value)
    plt.show()



def temp():
    # data

    start = dt(2017, 1, 1, 0, 0, 0, 0, pytz.utc)
    end = dt(2017, 9, 29, 0, 0, 0, 0, pytz.utc)

    data = web.DataReader("종가", "yahoo", start, end)

    data = data[['Adj Close']]
    data.columns = ['종가']
    # data = data.tz_localize('UTC')

    # algo = TradingAlgorithm(initialize=initialize, handle_data=handle_data)
    # result = algo.run(data)
    result = run_algorithm(start, end, initialize,100000000.0, handle_data,data_frequency = 'daily', data=data)

    # plt.plot(result.index, result.portfolio_value)
    # plt.show()

    plt.plot(result.index, result.ma5)
    plt.plot(result.index, result.ma20)
    plt.legend(loc='best')

    # plt.plot(result.ix[result.buy == True].index, result.ma5[result.buy == True], '^')
    # plt.plot(result.ix[result.sell == True].index, result.ma5[result.sell == True], 'v')

    plt.show()


def temp2():
    df = pd.read_hdf("test100.hdf", "day")
    datelen = len(df)

    # start = dt.strptime("20170101%s"%("000000"), "%Y%m%d%H%M%S").astimezone(pytz.utc)
    # end = dt.strptime("20170410%s"%("000000"), "%Y%m%d%H%M%S").astimezone(pytz.utc)

    start = dt(2017, 1, 1, 0, 0, 0, 0, pytz.utc)
    end = dt(2017, 4, 10, 0, 0, 0, 0, pytz.utc)

    # start = datetime.datetime(2017, 1, 1)
    # end = datetime.datetime(2017, 4, 10)

    # data = web.DataReader("종가", "yahoo", start, end)

    # rawdata = [ aa for aa in range(datelen)]
    rawdata = df["현재가"].tolist()
    # daterange = pd.date_range('2017/1/1', periods=datelen)
    daterange = pd.date_range(start, end)
    data = pd.DataFrame(rawdata, daterange, ['종가'])
    # data = data.tz_localize('UTC')

    result = run_algorithm(start, end, initialize,100000000.0, handle_data,data_frequency = 'daily', data=data)

    # algo = TradingAlgorithm(initialize=initialize, handle_data=handle_data)
    # result = algo.run(data)

    plt.plot(result.index, result.ma5)
    plt.plot(result.index, result.ma20)
    plt.legend(loc='best')


    plt.show()


if __name__ == "__main__" :
    temp2()