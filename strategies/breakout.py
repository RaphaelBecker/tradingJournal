import backtrader as bt

class BreakoutStrategy(bt.Strategy):
    params = dict(
        breakout_period=20,  # look back period for highest high - the breakout level
        close_period=10   # look back period for lowest low - the close level
    )

    def __init__(self):
        self.data_close = self.datas[0].close

        # Define the indicators
        self.highest_high = bt.indicators.Highest(self.data_close(-1), period=self.params.breakout_period)
        self.lowest_low = bt.indicators.Lowest(self.data_close(-1), period=self.params.close_period)

    def next(self):
        if not self.position:  # if we are not in the market
            if self.data_close > self.highest_high:
                self.buy()  # enter long

        elif self.data_close < self.lowest_low:
            self.close()  # close long position
