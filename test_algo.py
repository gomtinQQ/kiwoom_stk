from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import datetime  # For datetime objects

# Import the backtrader platform
import backtrader as bt
import pandas as pd



class TestStrategy_SMA(bt.Strategy):
    params = ( ('maperiod', 20), ('printlog', False), )

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
        self.smaClose = bt.indicators.SimpleMovingAverage(self.datas[0], period=5)
        # self.smaVolume = bt.indicators.SimpleMovingAverage(self.datas[0].volume, period=self.params.maperiod)

        # Indicators for the plotting show
        # bt.indicators.ExponentialMovingAverage(self.datas[0], period=5)
        # bt.indicators.WeightedMovingAverage(self.datas[0], period=5)
        # bt.indicators.StochasticSlow(self.datas[0])
        bt.indicators.MACDHisto(self.datas[0])
        # rsi = bt.indicators.RSI(self.datas[0])
        # bt.indicators.SmoothedMovingAverage(rsi, period=5 )
        # bt.indicators.ATR(self.datas[0] )

    def notify_order(self, order):
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
        if not trade.isclosed:
            return

        self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' %
                 (trade.pnl, trade.pnlcomm))

    def prenext(self):
        print('prenext:: current period:',  len(self), self.datas[0].datetime.date(0))
        pass

    def nextstart(self):
        print('nextstart:: current period:', len(self), self.datas[0].datetime.date(0))
        pass

    def next(self):
        # Simply log the closing price of the series from the reference
        print('next:: current period:', len(self), self.datas[0].datetime.date(0))

        self.log('Close, %.2f' % self.dataclose[0])

        # Check if an order is pending ... if yes, we cannot send a 2nd one
        if self.order:
            return

        # Check if we are in the market
        if not self.position:

            # Not yet ... we MIGHT BUY if ...
            if self.dataclose[0] > self.smaClose[0]:

                # BUY, BUY, BUY!!! (with all possible default parameters)
                self.log('BUY CREATE, %.2f' % self.dataclose[0])

                # Keep track of the created order to avoid a 2nd order
                self.order = self.buy()

        else:

            if self.dataclose[0] < self.smaClose[0]:
                # SELL, SELL, SELL!!! (with all possible default parameters)
                self.log('SELL CREATE, %.2f' % self.dataclose[0])

                # Keep track of the created order to avoid a 2nd order
                self.order = self.sell()

    def stop(self):
        """
        optstrategy을 사용한다면,  각 MA Period이 끝나는 시점에서  stop()이 called 된다.
        :return:
        """
        self.log('(MA Period %2d) Ending Value %.2f' % (self.params.maperiod, self.broker.getvalue()), doprint=True)

class TestStrategy_MACD(bt.Strategy):
    params = ( ('maperiod', 20), ('printlog', False),
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

        # To keep track of pending orders and buy price/commission
        self.order = None
        self.buyprice = None
        self.buycomm = None

        # Add a MovingAverageSimple indicator
        self.smaClose = bt.indicators.SimpleMovingAverage(self.datas[0], period=5)
        # self.smaVolume = bt.indicators.SimpleMovingAverage(self.datas[0].volume, period=self.params.maperiod)

        # Indicators for the plotting show
        # bt.indicators.ExponentialMovingAverage(self.datas[0], period=5)
        # bt.indicators.WeightedMovingAverage(self.datas[0], period=5)
        # bt.indicators.StochasticSlow(self.datas[0])
        macd = bt.indicators.MACDHisto(self.datas[0], period_me1=self.p.macd1,
                           period_me2=self.p.macd2,
                           period_signal=self.p.macdsig )

        # Cross of macd.macd and macd.signal
        self.macdsig = bt.ind.CrossOver(macd.macd, macd.signal)

        # rsi = bt.indicators.RSI(self.datas[0])
        # bt.indicators.SmoothedMovingAverage(rsi, period=5 )
        # bt.indicators.ATR(self.datas[0] )

    def notify_order(self, order):
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
        if not trade.isclosed:
            return

        self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' %
                 (trade.pnl, trade.pnlcomm))

    def prenext(self):
        print('prenext:: current period:',  len(self), self.datas[0].datetime.date(0))
        pass

    def nextstart(self):
        print('nextstart:: current period:', len(self), self.datas[0].datetime.date(0))
        pass

    def next(self):
        # Simply log the closing price of the series from the reference
        print('next:: current period:', len(self), self.datas[0].datetime.date(0))

        self.log('Close, %.2f' % self.dataclose[0])

        # Check if an order is pending ... if yes, we cannot send a 2nd one
        if self.order:
            return

        # Check if we are in the market
        if not self.position:

            # Not yet ... we MIGHT BUY if ...
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
        """
        optstrategy을 사용한다면,  각 MA Period이 끝나는 시점에서  stop()이 called 된다.
        :return:
        """
        self.log('(MA Period %2d) Ending Value %.2f' % (self.params.maperiod, self.broker.getvalue()), doprint=True)

if __name__ == '__main__':
    # Create a cerebro entity
    cerebro = bt.Cerebro()

    # Add a strategy
    bool_opti_strategy = False
    if bool_opti_strategy :
        strats = cerebro.optstrategy( TestStrategy_MACD, maperiod=range(10, 15))
    else:
        cerebro.addstrategy(TestStrategy_MACD)

    # Datas are in a subfolder of the samples. Need to find where the script is
    df = pd.read_hdf("000300.hdf", 'day').sort_index()
    serialdatetime = [datetime.datetime.strptime(str(bb), "%Y%m%d") for bb in df.index]
    df = df.set_index(pd.DatetimeIndex(serialdatetime))
    data = df[["현재가", "거래량", "시가", "고가", "저가"]]
    data.columns = ['close', 'volume', 'open', 'high', 'low']

    data = bt.feeds.PandasData(dataname=data, timeframe=1, openinterest=None)


    # Add the Data Feed to Cerebro
    cerebro.adddata(data)

    # Set our desired cash start
    cerebro.broker.setcash(100000000.0)

    # Add a FixedSize sizer according to the stake
    cerebro.addsizer(bt.sizers.FixedSize, stake=10)

    # Set the commission
    cerebro.broker.setcommission(commission=0.00165)

    # Print out the starting conditions
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

    # Run over everything
    cerebro.run()

    # Print out the final result
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

    # # Plot the result
    if bool_opti_strategy == False:
        cerebro.plot()