import backtrader as bt

class FollowInstitutions(bt.Strategy):
    # ADD the parameters here -----------------------------------------------------------------------------------------
    params = (
        ('volume_factor', 1.5),
        ('volume_average_length', 20),
    )
    # -----------------------------------------------------------------------------------------------------------------

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

        # ADD the Indicators here -----------------------------------------------------------------------------------------
        # Calculate average volume using Simple Moving Average (SMA)
        self.sma_volume = bt.indicators.SimpleMovingAverage(
            self.data.volume, period=self.params.volume_average_length
        )
        # On Balance Volume (OBV) indicator
        self.obv = bt.indicators.OnBalanceVolume(self.data)
        # -----------------------------------------------------------------------------------------------------------------


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

            # ADD buy Conditions here ----------------------------------------------------------------------------------
            if self.data.volume[0] > self.params.volume_factor * self.sma_volume[0]:
                if self.data.close[0] > self.data.close[-1] and self.obv[0] > self.obv[-1]:
                    self.buy()  # Institutional buying may be happening
                    self.log('BUY CREATE, %.2f' % self.dataclose[0])
                elif self.data.close[0] < self.data.close[-1] and self.obv[0] < self.obv[-1]:
                    self.sell()  # Institutional selling may be happening
                    self.log('SELL CREATE, %.2f' % self.dataclose[0])
                # ------------------------------------------------------------------------------------------------------

        else:

            # ADD sell Conditions here ---------------------------------------------------------------------------------
            if (self.position.size > 0 and self.obv[0] < self.obv[-1]) or (
                    self.position.size < 0 and self.obv[0] > self.obv[-1]
            ):
                self.close()  # Exit the position if OBV goes against our position

                # ------------------------------------------------------------------------------------------------------
                self.log('EXIT POSITION, %.2f' % self.dataclose[0])
