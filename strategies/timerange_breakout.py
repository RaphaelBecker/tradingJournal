import backtrader as bt

class BreakoutStrategy(bt.Strategy):
    # ADD the parameters here -----------------------------------------------------------------------------------------
    params = dict(
        breakout_period=15,  # look back period for highest high - the breakout level
        close_period=8  # look back period for lowest low - the close level
    )
    # -----------------------------------------------------------------------------------------------------------------

    def log(self, txt, dt=None):
        ''' Logging function fot this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        # Keep a reference to the "close" line in the data[0] dataseries
        self.data_close = self.datas[0].close

        # To keep track of pending orders and buy price/commission
        self.order = None
        self.buyprice = None
        self.buycomm = None

        # Add Indicators here
        self.highest_high = bt.indicators.Highest(self.data_close(-1), period=self.params.breakout_period)
        self.lowest_low = bt.indicators.Lowest(self.data_close(-1), period=self.params.close_period)
        self.rsi = bt.indicators.RSI(self.data_close)
        self.sma100 = bt.indicators.SmoothedMovingAverage(self.data_close, period=100)
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

        if not self.position:  # if we are not in the market
            if self.data_close > self.highest_high:
                self.buy()  # enter long

        elif self.data_close < self.lowest_low:
            self.close()  # close long position