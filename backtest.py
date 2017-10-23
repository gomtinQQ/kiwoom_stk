# /usr/bin/python3
#-*- coding: utf-8 -*-
#Author : jaehyek Choi
# 목적 : zipline을 활용하여,  만들거나 만든 트레이딩 알고리즘을 검증한다.
# zipline은  https://github.com/jaehyek/zipline 처음에 설치방법에 대해
# 설명을 했다. Python 3.6 32bit 으로.
# 키움증권 OCX 가 32bit이므로 우리가 사용하는 환경은  32bit이다.
#---------------------------------------------------------

import pandas_datareader.data as web
import datetime
import matplotlib.pyplot as plt
from zipline.api import order, symbol
from zipline.algorithm import TradingAlgorithm

# data
start = datetime.datetime(2016, 1, 1)
end = datetime.datetime(2016, 12, 19)
data = web.DataReader("AAPL", "yahoo", start, end)

data = data[['Adj Close']]
data.columns = ['AAPL']

#아래를 사용하면,
#  KeyError: 'the label [2009-12-31 00:00:00+00:00] is not in the [index]'
# 라고 error가 뜬다. 사용하지 않는다. 당분간 사용하지 않는다.
data = data.tz_localize('UTC')

def initialize(context):
    pass

def handle_data(context, data):
    order(symbol('AAPL'), 1)

algo = TradingAlgorithm(initialize=initialize, handle_data=handle_data)
result = algo.run(data)

serialdatetime = pd.Series([pd.to_datetime(bb, format="%Y%m%d") for bb in df.index ])
df2 = df.set_index(serialdatetime)

plt.plot(result.index, result.portfolio_value)
plt.show()
