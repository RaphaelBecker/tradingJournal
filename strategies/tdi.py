import backtrader as bt

class TDI(bt.Strategy):
    params = (
        ('maperiod', 200),
    )

    def log(self, txt, dt=None):
        ''' Logging function fot this strategy'''
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
        self.sma = bt.indicators.SimpleMovingAverage(
            self.datas[0], period=self.params.maperiod)

        # Indicators for the plotting show

        # Indicators for the plotting show
        # TDI --------------------------------------------------
        self.rsi = bt.indicators.RSI(self.datas[0])
        self.smoothedSMA = bt.indicators.SmoothedMovingAverage(self.rsi, period=10)
        # Bollinger
        self.bb = bt.indicators.BollingerBands(self.rsi)
        self.bull_rsi_bb_crossover = bt.ind.CrossOver(self.rsi, self.smoothedSMA)
        self.bear_rsi_bb_crossover = bt.ind.CrossOver(self.smoothedSMA, self.rsi)
        # self.bb.top[0]
        # self.bb.bottom[0]

        # ------------------------------------------------------
        # MACD
        self.macd = bt.indicators.MACDHisto(self.datas[0])
        # ATR
        #bt.indicators.ATR(self.datas[0], plot=True)
        # PIVOT
        self.pivotindicator = bt.indicators.FibonacciPivotPoint(self.data1)

        #bt.indicators.ExponentialMovingAverage(self.datas[0], period=25)
        #bt.indicators.WeightedMovingAverage(self.datas[0], period=25,
        #                                    subplot=True)
        #bt.indicators.StochasticSlow(self.datas[0])

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
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

        elif order.status == order.Canceled:
            self.log('Order Canceled')
        elif order.status == order.Margin:
            self.log('Order Margin')
        elif order.status == order.Rejected:
            self.log('Order Rejected')

        # Write down: no pending order
        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' %
                 (trade.pnl, trade.pnlcomm))

    def next(self):

        # Check if an order is pending ... if yes, we cannot send a 2nd one
        if self.order:
            return

        # Check if we are in the market
        if not self.position:

            # Not yet ... we MIGHT BUY if ...
            #if self.dataclose[0] > self.sma[0]:
            if self.rsi[0] <= 48 and self.bull_rsi_bb_crossover[0] and \
                    self.pivotindicator.s2[0] > self.dataclose[0] > self.pivotindicator.s3[0]:
                # BUY, BUY, BUY!!! (with all possible default parameters)
                self.log('BUY CREATE, %.2f' % self.dataclose[0])

                # Keep track of the created order to avoid a 2nd order
                self.order = self.buy()

        else:

            #if self.dataclose[0] < self.sma[0]:
            if self.rsi[0] > 62 and self.bear_rsi_bb_crossover[0]and \
                    self.pivotindicator.r2[0] < self.dataclose[0] < self.pivotindicator.r3[0]:
                # SELL, SELL, SELL!!! (with all possible default parameters)
                self.log('SELL CREATE, %.2f' % self.dataclose[0])

                # Keep track of the created order to avoid a 2nd order
                self.order = self.sell()