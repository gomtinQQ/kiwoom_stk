from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import datetime  # For datetime objects
import os.path  # To manage paths
import sys  # To find out the script name (in argv[0])

# Import the backtrader platform
# refer to https://www.backtrader.com/docu/index.html
import backtrader as bt
import pandas as pd
import utils
import numpy as np
from scipy.stats import norm, normaltest

# Create a Stratey
class Strategy_ma5_ma20_MovingAverageMethod(bt.Strategy):

    params = (
        ('maPeriodShort', 5),
        ('maPeriodLong', 20),
        ('printlog', False),
        ('code', ""),
        ('strfilename', ""),
        ('MovingAverageMethodShort', "SimpleMovingAverage"),
        ('MovingAverageMethodLong', "SimpleMovingAverage"),

    )

    def log(self, txt, dt=None, doprint=False):
        ''' Logging function fot this strategy'''
        if self.params.printlog or doprint:
            dt = dt or self.datas[0].datetime.date(0)
            print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        # Keep a reference to the "close" line in the data[0] dataseries
        self.dataclose = self.datas[0].close

        # To keep track of pending orders and buy price/commission
        self.order = None
        self.buyprice = None
        self.buycomm = None

        # Add a MovingAverageSimple indicator
        if (self.params.MovingAverageMethodShort == "SimpleMovingAverage"):
            self.smaShort = bt.indicators.SimpleMovingAverage(self.datas[0], period=self.params.maPeriodShort)
        elif (self.params.MovingAverageMethodShort == "ExponentialMovingAverage"):
            self.smaShort = bt.indicators.ExponentialMovingAverage(self.datas[0], period=self.params.maPeriodShort)
        elif (self.params.MovingAverageMethodShort == "WeightedMovingAverage"):
            self.smaShort = bt.indicators.WeightedMovingAverage(self.datas[0], period=self.params.maPeriodShort)

        if (self.params.MovingAverageMethodLong == "SimpleMovingAverage"):
            self.smaLong = bt.indicators.SimpleMovingAverage(self.datas[0], period=self.params.maPeriodLong)
        elif (self.params.MovingAverageMethodLong == "ExponentialMovingAverage"):
            self.smaLong = bt.indicators.ExponentialMovingAverage(self.datas[0], period=self.params.maPeriodLong)
        elif (self.params.MovingAverageMethodLong == "WeightedMovingAverage"):
            self.smaLong = bt.indicators.WeightedMovingAverage(self.datas[0], period=self.params.maPeriodLong)


        # # Indicators for the plotting show
        # bt.indicators.ExponentialMovingAverage(self.datas[0], period=25)
        # bt.indicators.WeightedMovingAverage(self.datas[0], period=25,subplot=True)
        # bt.indicators.StochasticSlow(self.datas[0])
        # bt.indicators.MACDHisto(self.datas[0])
        # rsi = bt.indicators.RSI(self.datas[0])
        # bt.indicators.SmoothedMovingAverage(rsi, period=10)
        # bt.indicators.ATR(self.datas[0], plot=False)

    def notify_order(self, order):
        """
        Receives an order whenever there has been a change in one
        :param order:
        :return:
        """
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enougth cash
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    'BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                    (order.executed.price,
                     order.executed.value,
                     order.executed.comm))

                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            else:  # Sell
                self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                         (order.executed.price,
                          order.executed.value,
                          order.executed.comm))

            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        # Write down: no pending order
        self.order = None

    def notify_trade(self, trade):
        """
        Receives a trade whenever there has been a change in one
        :param trade:
        :return:
        """
        if not trade.isclosed:
            return

        self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' % (trade.pnl, trade.pnlcomm))
        # pnl (float)    : current profit and loss of the trade (gross pnl)
        # pnlcomm (float): current profit and loss of the trade minus commission (net pnl)

    def prenext(self):
        # print('prenext:: current period:',  len(self), self.datas[0].datetime.date(0))
        pass

    def nextstart(self):
        # print('nextstart:: current period:', len(self), self.datas[0].datetime.date(0))
        pass

    def next(self):
        """
        This method will be called for all remaining data points when the minimum period for all datas/indicators have been meet.
        :return:
        """

        # Simply log the closing price of the series from the reference
        self.log('Close, %.2f' % self.dataclose[0])

        # Check if an order is pending ... if yes, we cannot send a 2nd one
        if self.order:
            return

        # Check if we are in the market
        if not self.position:

            # Not yet ... we MIGHT BUY if ...
            if self.smaShort[0] > self.smaLong[0]:

                # BUY, BUY, BUY!!! (with all possible default parameters)
                self.log('BUY CREATE, %.2f' % self.dataclose[0])

                # Keep track of the created order to avoid a 2nd order
                self.order = self.buy()

        else:

            if self.smaShort[0] < self.smaLong[0]:
                # SELL, SELL, SELL!!! (with all possible default parameters)
                self.log('SELL CREATE, %.2f' % self.dataclose[0])

                # Keep track of the created order to avoid a 2nd order
                self.order = self.sell()

    def stop(self):
        try:

            self.log('(MA Period %2d, %2d) Ending Value %.2f' % (self.params.maPeriodShort,self.params.maPeriodLong, self.broker.getvalue()), doprint=True)
            historytrades = list(list(self._trades.copy().values())[0].values())[0]
            nstake = self.getsizer().params.stake
            listprofitrate = []
            for dealtemp in historytrades:
                cost = nstake * dealtemp.price
                netprofit = dealtemp.pnlcomm
                listprofitrate.append(netprofit / cost)
            mean = np.mean(listprofitrate)
            std = np.std(listprofitrate)
            _, pvalue = normaltest(listprofitrate)
            # 원래의 cost에 비해서 net-profit 의 rate 을 구하고,  이 rate의 평균과 표준분산을 구해서,
            # 평균 얼마의 승률이 있는지 cdf을 이용해서 구한다.
            # 승률이  50%이면 본전이므로,  최소한 > 50% 이어야 한다.
            print("N:%s, mean:%s, std:%s, profitable rate : %s, p-value:%.2f" % (len(listprofitrate), mean, std, 1 - norm.cdf(-mean / std), pvalue))
            if ( pvalue < 0.05) :
                f_csv = open(self.params.strfilename, "a", encoding='utf-8')
                strcsvout = "%s,%s,%s,%s,%s,%s,%s,%s,%.2f\n"%(self.params.code,self.params.maPeriodShort,self.params.maPeriodLong,self.broker.getvalue(),len(listprofitrate), mean, std, 1 - norm.cdf(-mean / std), pvalue )
                f_csv.write(strcsvout)
                f_csv.close()
        except:
            pass

if __name__ == '__main__':

    timeprev = datetime.datetime.now()
    strfilename = "smExponential.csv"
    # strfilename = "highvolume.csv"
    if os.path.exists(strfilename) == True:
        os.remove(strfilename)

    listcode = utils.get_list_code()
    # listcode = ["000300"]
    lencode = len(listcode)
    countleft = lencode


    for code in listcode:
        try :
            print("--------------------------- %s/%s, code : %s ----------------------------"%(countleft,  lencode, code ))
            countleft -= 1
            df = utils.get_dataframe_with_code(code)
            cerebro = bt.Cerebro()

            # Add a strategy
            # cerebro.addstrategy(TestStrategy)
            cerebro.optstrategy(Strategy_ma5_ma20_MovingAverageMethod, maPeriodShort=range(5,15), maPeriodLong=range(15, 50),
                                code=code, strfilename=strfilename, MovingAverageMethodShort="ExponentialMovingAverage", MovingAverageMethodLong="ExponentialMovingAverage" )

            serialdatetime = [datetime.datetime.strptime(str(bb), "%Y%m%d") for bb in df.index]
            df = df.set_index(pd.DatetimeIndex(serialdatetime))
            data = df[["현재가", "거래량", "시가", "고가", "저가"]]
            data.columns = ['close', 'volume', 'open', 'high', 'low']

            data = bt.feeds.PandasData(dataname=data, timeframe=1, openinterest=None)

            # Add the Data Feed to Cerebro
            cerebro.adddata(data)

            # Set our desired cash start
            # cash단위가 원으로 되므로  1억으로 확대한다.
            cerebro.broker.setcash(100000000.0)

            # Add a FixedSize sizer according to the stake
            cerebro.addsizer(bt.sizers.FixedSize, stake=10)

            # Set the commission
            # 매도거래세 : 0.3%,  매도매수수수료:0.165%  -> total : 0.33%
            # 매수 매도에 둘로 나누면, 0.165%가 된다.
            cerebro.broker.setcommission(commission=0.00165)

            # Print out the starting conditions
            print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

            # Run over everything
            listliststrategy = cerebro.run()

            # Print out the final result
            print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
        except:
            f = open("error.log", "a", encoding='utf-8')
            f.write("error code is %s\n"%(code))
            f.close()
            pass


    print("Elapse time is %s "%(datetime.datetime.now() - timeprev ))
    # Plot the result
    # cerebro.plot()



