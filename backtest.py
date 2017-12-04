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
import argparse


class Strategy_ma5_ma20_MovingAverageMethod(bt.Strategy):
    """
    목적 : 3가지 type의 Moving Average을 통해서  profit이 가장 좋은 조합을 구한다. 
    ma5 : moving average short term 
    ma20: moving average long term 
    이 두 moving average은 계산시,   SimpleMovingAverage, ExponentialMovingAverage, WeightedMovingAverage 을 각각 적용하다.
    """

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
            self.maShort = bt.indicators.SimpleMovingAverage(self.datas[0], period=self.params.maPeriodShort)
        elif (self.params.MovingAverageMethodShort == "ExponentialMovingAverage"):
            self.maShort = bt.indicators.ExponentialMovingAverage(self.datas[0], period=self.params.maPeriodShort)
        elif (self.params.MovingAverageMethodShort == "WeightedMovingAverage"):
            self.maShort = bt.indicators.WeightedMovingAverage(self.datas[0], period=self.params.maPeriodShort)

        if (self.params.MovingAverageMethodLong == "SimpleMovingAverage"):
            self.maLong = bt.indicators.SimpleMovingAverage(self.datas[0], period=self.params.maPeriodLong)
        elif (self.params.MovingAverageMethodLong == "ExponentialMovingAverage"):
            self.maLong = bt.indicators.ExponentialMovingAverage(self.datas[0], period=self.params.maPeriodLong)
        elif (self.params.MovingAverageMethodLong == "WeightedMovingAverage"):
            self.maLong = bt.indicators.WeightedMovingAverage(self.datas[0], period=self.params.maPeriodLong)


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
            if self.maShort[0] > self.maLong[0]:

                # BUY, BUY, BUY!!! (with all possible default parameters)
                self.log('BUY CREATE, %.2f' % self.dataclose[0])

                # Keep track of the created order to avoid a 2nd order
                self.order = self.buy()

        else:

            if self.maShort[0] < self.maLong[0]:
                # SELL, SELL, SELL!!! (with all possible default parameters)
                self.log('SELL CREATE, %.2f' % self.dataclose[0])

                # Keep track of the created order to avoid a 2nd order
                self.order = self.sell()

    def stop(self):
        try:
            f_csv = open(self.params.strfilename, "a", encoding='utf-8')
            historytrades = list(list(self._trades.copy().values())[0].values())[0]
            nstake = self.getsizer().params.stake
            listprofitrate = []
            for dealtemp in historytrades:
                cost = nstake * dealtemp.price
                netprofit = dealtemp.pnlcomm
                profitrate = netprofit / cost
                listprofitrate.append(profitrate)
                strcsvout = "%s,%s,%s,%s,%.5f\n" % (
                    self.params.code, self.params.maPeriodShort, self.params.maPeriodLong, "rate", profitrate )
                f_csv.write(strcsvout)

            mean = np.mean(listprofitrate)
            std = np.std(listprofitrate)
            _, pvalue = normaltest(listprofitrate)
            strcsvout = "%s,%s,%s,%s,%s,%s,%.5f,%.5f,%.5f,%.5f\n"%(self.params.code, self.params.maPeriodShort, self.params.maPeriodLong,
                        "sum", self.broker.getvalue(), len(listprofitrate), mean, std, 1 - norm.cdf(-mean / std), pvalue  )
            f_csv.write(strcsvout)
            f_csv.close()

            self.log('code=%s ma5=%s ma20=%s profit=%.2f' % (self.params.code, self.params.maPeriodShort, self.params.maPeriodLong,
                    self.broker.getvalue()), doprint=True)
        except:
            pass

def backtracer_MovingAverage(strfilename,listcode):
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
            cerebro.optstrategy(Strategy_ma5_ma20_MovingAverageMethod, maPeriodShort=range(9,15), maPeriodLong=range(15, 50),
                                code=code, strfilename=strfilename, MovingAverageMethodShort="SimpleMovingAverage", MovingAverageMethodLong="SimpleMovingAverage" )

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

    # Plot the result
    # cerebro.plot()

## --------------------------------------------------------------

class Strategy_ma5_ma20_VolumeAverageMethod(bt.Strategy):
    """
    목적 : 매수시 급등주를 발굴하고, 매도시 3가지 type의 Moving Average을 이용하여,  profit이 가장 좋은 조합을 구한다. 
    ma5 : moving average short term 
    ma20: moving average long term 
    mav : moving average volume 
    volmx : current volume comparison multiple to the previous volume average   
    """

    params = (
        ('maPeriodShort', 5),
        ('maPeriodLong', 20),
        ('printlog', False),
        ('code', ""),
        ('strfilename', ""),
        ('MovingAverageMethodShort', "SimpleMovingAverage"),
        ('MovingAverageMethodLong', "SimpleMovingAverage"),
        ('MovingAverageVolume', "SimpleMovingAverage"),
        ('maVolPeriod', 20),
        ('VolumeMultiple', 5),
    )

    def log(self, txt, dt=None, doprint=False):
        ''' Logging function fot this strategy'''
        if self.params.printlog or doprint:
            dt = dt or self.datas[0].datetime.date(0)
            print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        # Keep a reference to the "close" line in the data[0] dataseries
        self.dataclose = self.datas[0].close
        self.datavolume = self.datas[0].volume

        # To keep track of pending orders and buy price/commission
        self.order = None
        self.buyprice = None
        self.buycomm = None
        self.VolumeMultiple = self.params.VolumeMultiple

        # Add a MovingAverageSimple indicator
        if (self.params.MovingAverageMethodShort == "SimpleMovingAverage"):
            self.maShort = bt.indicators.SimpleMovingAverage(self.datas[0], period=self.params.maPeriodShort)
        elif (self.params.MovingAverageMethodShort == "ExponentialMovingAverage"):
            self.maShort = bt.indicators.ExponentialMovingAverage(self.datas[0], period=self.params.maPeriodShort)
        elif (self.params.MovingAverageMethodShort == "WeightedMovingAverage"):
            self.maShort = bt.indicators.WeightedMovingAverage(self.datas[0], period=self.params.maPeriodShort)

        if (self.params.MovingAverageMethodLong == "SimpleMovingAverage"):
            self.maLong = bt.indicators.SimpleMovingAverage(self.datas[0], period=self.params.maPeriodLong)
        elif (self.params.MovingAverageMethodLong == "ExponentialMovingAverage"):
            self.maLong = bt.indicators.ExponentialMovingAverage(self.datas[0], period=self.params.maPeriodLong)
        elif (self.params.MovingAverageMethodLong == "WeightedMovingAverage"):
            self.maLong = bt.indicators.WeightedMovingAverage(self.datas[0], period=self.params.maPeriodLong)

        if (self.params.MovingAverageMethodLong == "SimpleMovingAverage"):
            self.maVolume = bt.indicators.SimpleMovingAverage(self.datas[0], period=self.params.maVolPeriod)
        elif (self.params.MovingAverageMethodLong == "ExponentialMovingAverage"):
            self.maVolume = bt.indicators.ExponentialMovingAverage(self.datas[0], period=self.params.maVolPeriod)
        elif (self.params.MovingAverageMethodLong == "WeightedMovingAverage"):
            self.maVolume = bt.indicators.WeightedMovingAverage(self.datas[0], period=self.params.maVolPeriod)


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

        # print('next:: current period:', len(self), self.datas[0].datetime.date(0))

        # Simply log the closing price of the series from the reference
        self.log('Close, %.2f' % self.dataclose[0])

        # Check if an order is pending ... if yes, we cannot send a 2nd one
        if self.order:
            return

        # Check if we are in the market
        if not self.position:

            if (self.datavolume[0] >=  self.maVolume[0] * self.VolumeMultiple) and (self.maShort[0] > self.maLong[0]) :

                # BUY, BUY, BUY!!! (with all possible default parameters)
                self.log('BUY CREATE, %.2f' % self.dataclose[0])

                # Keep track of the created order to avoid a 2nd order
                self.order = self.buy()

        else:

            if self.maShort[0] < self.maLong[0]:
                # SELL, SELL, SELL!!! (with all possible default parameters)
                self.log('SELL CREATE, %.2f' % self.dataclose[0])

                # Keep track of the created order to avoid a 2nd order
                self.order = self.sell()

    def stop(self):
        try:
            f_csv = open(self.params.strfilename, "a", encoding='utf-8')
            historytrades = list(list(self._trades.copy().values())[0].values())[0]
            nstake = self.getsizer().params.stake
            listprofitrate = []
            for dealtemp in historytrades:
                cost = nstake * dealtemp.price
                netprofit = dealtemp.pnlcomm
                profitrate = netprofit / cost
                listprofitrate.append(profitrate)
                strcsvout = "%s,%s,%s,%s,%s,%s,%.5f\n" % (
                    self.params.code, self.params.maPeriodShort, self.params.maPeriodLong,
                    self.params.maVolPeriod, self.params.VolumeMultiple, "rate", profitrate )
                f_csv.write(strcsvout)

            mean = np.mean(listprofitrate)
            std = np.std(listprofitrate)
            _, pvalue = normaltest(listprofitrate)
            strcsvout = "%s,%s,%s,%s,%s,%s,%s,%s,%.5f,%.5f,%.5f,%.5f\n"%(self.params.code, self.params.maPeriodShort, self.params.maPeriodLong,
                        self.params.maVolPeriod, self.params.VolumeMultiple, "sum", self.broker.getvalue(), len(listprofitrate),
                        mean, std, 1 - norm.cdf(-mean / std), pvalue  )
            f_csv.write(strcsvout)
            f_csv.close()

            self.log('code=%s ma5=%s ma20=%s mvol=%s  mvolmulti=%s profit=%.2f' % (self.params.code, self.params.maPeriodShort, self.params.maPeriodLong,
                    self.params.maVolPeriod, self.params.VolumeMultiple, self.broker.getvalue()), doprint=True)

        except:
            pass

        # try:
        #
        #     self.log('(MA Period %2d, %2d) Ending Value %.2f' % (self.params.maPeriodShort,self.params.maPeriodLong, self.broker.getvalue()), doprint=True)
        #     historytrades = list(list(self._trades.copy().values())[0].values())[0]
        #     nstake = self.getsizer().params.stake
        #     listprofitrate = []
        #     for dealtemp in historytrades:
        #         cost = nstake * dealtemp.price
        #         netprofit = dealtemp.pnlcomm
        #         listprofitrate.append(netprofit / cost)
        #     mean = np.mean(listprofitrate)
        #     std = np.std(listprofitrate)
        #     _, pvalue = normaltest(listprofitrate)
        #     # 원래의 cost에 비해서 net-profit 의 rate 을 구하고,  이 rate의 평균과 표준분산을 구해서,
        #     # 평균 얼마의 승률이 있는지 cdf을 이용해서 구한다.
        #     # 승률이  50%이면 본전이므로,  최소한 > 50% 이어야 한다.
        #     print("N:%s, mean:%s, std:%s, profitable rate : %s, p-value:%.2f" % (len(listprofitrate), mean, std, 1 - norm.cdf(-mean / std), pvalue))
        #     if ( pvalue < 0.05) :
        #         f_csv = open(self.params.strfilename, "a", encoding='utf-8')
        #         strcsvout = "%s,%s,%s,%s,%s,%s,%s,%s,%.2f,%s,%s\n"%(self.params.code,self.params.maPeriodShort,self.params.maPeriodLong,self.broker.getvalue(),len(listprofitrate),
        #                             mean, std, 1 - norm.cdf(-mean / std), pvalue,  self.params.maVolPeriod, self.params.VolumeMultiple )
        #         f_csv.write(strcsvout)
        #         f_csv.close()
        # except:
        #     pass

def backtracer_MovingAverage_Volume(strfilename,listcode):
    lencode = len(listcode)
    countleft = lencode


    for code in listcode:
        try :
            print("--------------------------- %s/%s, code : %s ----------------------------"%(countleft,  lencode, code ))
            countleft -= 1
            df = utils.get_dataframe_with_code(code)
            cerebro = bt.Cerebro()

            # Add a strategy
            # 1차 Try하기.
            # cerebro.optstrategy(Strategy_ma5_ma20_VolumeAverageMethod, maPeriodShort=range(9,15), maPeriodLong=range(41, 50),
            #                     code=code, strfilename=strfilename, MovingAverageMethodShort="SimpleMovingAverage", MovingAverageMethodLong="SimpleMovingAverage",
            #                     MovingAverageVolume="SimpleMovingAverage", VolumeMultiple=[1.5, 2, 3, 4, 5, 8, 10, 15, 20], maVolPeriod=[30,40,50,60])

            # 위의 simulation에서 결론은  최고의 수익률이 0.055 정도의 평균수익률이 나왔다.
            # 수익률 대비 가능한  변수 범위를 아래와 같이 정하고 추가 simulation을 진행한다.
            # 결과적으로 maVolPeriod=[ 30, 40], VolumeMultiple=[15,20], maPeriodLong=[47,48,49], maPeriodShort=[11,12,13,15] 이나,
            # 변수를 추가 확대하여 simulation한다.
            cerebro.optstrategy(Strategy_ma5_ma20_VolumeAverageMethod, maPeriodShort=[11,12,13,15,17,19,21],
                                maPeriodLong=[47,49,51,53,55,57,9],
                                code=code, strfilename=strfilename, MovingAverageMethodShort="SimpleMovingAverage",
                                MovingAverageMethodLong="SimpleMovingAverage",
                                MovingAverageVolume="SimpleMovingAverage",
                                VolumeMultiple=[15,17,19,21,23,25,30], maVolPeriod=[29,31,33,35,37,39,41,43,45,47])

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

## --------------------------------------------------------------


class Strategy_MACD(bt.Strategy):
    """
    목적 : 일반적인 MACD을 수행한다.
    """

    params = (
        ('printlog', False),
        ('code', ""),
        ('strfilename', ""),
        ('macd1', 12),
        ('macd2', 26),
        ('macdsig', 9),
    )

    def log(self, txt, dt=None, doprint=False):
        ''' Logging function fot this strategy'''
        if self.params.printlog or doprint:
            dt = dt or self.datas[0].datetime.date(0)
            print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        # Keep a reference to the "close" line in the data[0] dataseries
        self.dataclose = self.datas[0].close
        self.datavolume = self.datas[0].volume

        # To keep track of pending orders and buy price/commission
        self.order = None
        self.buyprice = None
        self.buycomm = None

        macd = bt.indicators.MACDHisto(self.datas[0], period_me1=self.p.macd1,
                                       period_me2=self.p.macd2,
                                       period_signal=self.p.macdsig)

        # Cross of macd.macd and macd.signal
        self.macdsig = bt.ind.CrossOver(macd.macd, macd.signal)


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

        # print('next:: current period:', len(self), self.datas[0].datetime.date(0))

        # Simply log the closing price of the series from the reference
        self.log('Close, %.2f' % self.dataclose[0])

        # Check if an order is pending ... if yes, we cannot send a 2nd one
        if self.order:
            return

        # Check if we are in the market
        if not self.position:

            if self.macdsig[0] > 0.0:

                # BUY, BUY, BUY!!! (with all possible default parameters)
                self.log('BUY CREATE, %.2f' % self.dataclose[0])

                # Keep track of the created order to avoid a 2nd order
                self.order = self.buy()

        else:

            if self.macdsig[0] < 0.0:
                # SELL, SELL, SELL!!! (with all possible default parameters)
                self.log('SELL CREATE, %.2f' % self.dataclose[0])

                # Keep track of the created order to avoid a 2nd order
                self.order = self.sell()

    def stop(self):
        try:
            f_csv = open(self.params.strfilename, "a", encoding='utf-8')
            historytrades = list(list(self._trades.copy().values())[0].values())[0]
            nstake = self.getsizer().params.stake
            listprofitrate = []
            for dealtemp in historytrades:
                cost = nstake * dealtemp.price
                netprofit = dealtemp.pnlcomm
                profitrate = netprofit / cost
                listprofitrate.append(profitrate)
                strcsvout = "%s,%s,%s,%s,%s,%.5f\n" % ( self.params.code, self.p.macd1, self.p.macd2,
                    self.p.macdsig,  "rate", profitrate )
                f_csv.write(strcsvout)

            mean = np.mean(listprofitrate)
            std = np.std(listprofitrate)
            _, pvalue = normaltest(listprofitrate)
            strcsvout = "%s,%s,%s,%s,%s,%.5f,%s,%.5f,%.5f,%.5f,%.5f\n"%(self.params.code, self.p.macd1, self.p.macd2,
                        self.p.macdsig, "sum", self.broker.getvalue(), len(listprofitrate),
                        mean, std, 1 - norm.cdf(-mean / std), pvalue  )
            f_csv.write(strcsvout)
            f_csv.close()

            self.log('code=%s macd1=%s macd2=%s macdsig=%s  profit=%.2f' % (self.params.code, self.p.macd1, self.p.macd2,
                        self.p.macdsig,  self.broker.getvalue()), doprint=True)

        except:
            pass

        # try:
        #
        #     self.log('(MA Period %2d, %2d) Ending Value %.2f' % (self.params.maPeriodShort,self.params.maPeriodLong, self.broker.getvalue()), doprint=True)
        #     historytrades = list(list(self._trades.copy().values())[0].values())[0]
        #     nstake = self.getsizer().params.stake
        #     listprofitrate = []
        #     for dealtemp in historytrades:
        #         cost = nstake * dealtemp.price
        #         netprofit = dealtemp.pnlcomm
        #         listprofitrate.append(netprofit / cost)
        #     mean = np.mean(listprofitrate)
        #     std = np.std(listprofitrate)
        #     _, pvalue = normaltest(listprofitrate)
        #     # 원래의 cost에 비해서 net-profit 의 rate 을 구하고,  이 rate의 평균과 표준분산을 구해서,
        #     # 평균 얼마의 승률이 있는지 cdf을 이용해서 구한다.
        #     # 승률이  50%이면 본전이므로,  최소한 > 50% 이어야 한다.
        #     print("N:%s, mean:%s, std:%s, profitable rate : %s, p-value:%.2f" % (len(listprofitrate), mean, std, 1 - norm.cdf(-mean / std), pvalue))
        #     if ( pvalue < 0.05) :
        #         f_csv = open(self.params.strfilename, "a", encoding='utf-8')
        #         strcsvout = "%s,%s,%s,%s,%s,%s,%s,%s,%.2f,%s,%s\n"%(self.params.code,self.params.maPeriodShort,self.params.maPeriodLong,self.broker.getvalue(),len(listprofitrate),
        #                             mean, std, 1 - norm.cdf(-mean / std), pvalue,  self.params.maVolPeriod, self.params.VolumeMultiple )
        #         f_csv.write(strcsvout)
        #         f_csv.close()
        # except:
        #     pass

def backtracer_MACD(strfilename,listcode):
    lencode = len(listcode)
    countleft = lencode


    for code in listcode:
        try :
            print("--------------------------- %s/%s, code : %s ----------------------------"%(countleft,  lencode, code ))
            countleft -= 1
            df = utils.get_dataframe_with_code(code)
            cerebro = bt.Cerebro()

            cerebro.optstrategy(Strategy_MACD, code=code, strfilename=strfilename,
                                macd1=[8,10,12,14,16,18],
                                macd2=[20,22,24,26,28,30,32],
                                macdsig = [6,7,8,9,10,11,12,13]
                                )

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

## --------------------------------------------------------------

if __name__ == '__main__':
    cmdlineopt = argparse.ArgumentParser(description='filter row data from csv file ')
    cmdlineopt.add_argument('-m', action="store", dest="backtest_method", default='averagevolume', help='select the backtest method')
    cmdlineopt.add_argument('-s', action="store", dest="startcodeindex", default=None,help='start code index')
    cmdlineopt.add_argument('-e', action="store", dest="endcodeindex", default=None,help='end code index')
    cmdlineopt.add_argument('-f', action="store", dest="filename", default='filename.csv',help='csv filename to save')

    clsvar = cmdlineopt.parse_args()

    strfilename = clsvar.filename
    if os.path.exists(strfilename) == True:
        os.remove(strfilename)

    startindex = None if clsvar.startcodeindex == None else  int(clsvar.startcodeindex)
    endindex = None if clsvar.endcodeindex == None else  int(clsvar.endcodeindex)

    listcode = utils.get_list_code()            #  len(listcode) = 2595
    listcode = listcode[startindex:endindex]
    # listcode = ["000300"]

    timeprev = datetime.datetime.now()

    if clsvar.backtest_method == 'averagemoving' :
        backtracer_MovingAverage(strfilename,listcode )
    elif clsvar.backtest_method == 'averagevolume' :
        backtracer_MovingAverage_Volume(strfilename,listcode )
    elif clsvar.backtest_method == 'macd' :
        backtracer_MACD(strfilename,listcode )

    print("Elapse time is %s " % (datetime.datetime.now() - timeprev))

    #
