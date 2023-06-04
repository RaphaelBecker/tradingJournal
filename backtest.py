import streamlit as st
import yfinance as yf
import backtrader as bt
from backtrader.feeds import PandasData
import numpy as np


# Class to hold your custom fundamental/technical data
class ExtendedPandasData(PandasData):
    lines = (
        'price_to_earning',
        'price_to_book',
        'dept_to_equity',
        'free_cash_flow',
        'PEG_ratio',
        'RSI',
        'mac_d',
        'on_balance_volume',
        'AD_line',
        'ADX',
        'aroon_indicator',
    )
    params = ((col, -1) for col in lines)


# Your custom strategy
class TestStrategy(bt.Strategy):
    params = (
        ('maperiod', 15),
    )

    def __init__(self):
        self.dataclose = self.datas[0].close
        self.order = None

    def next(self):
        if self.order:
            return

        if not self.position:
            if self.dataclose[0] > self.dataclose[-1]:
                self.order = self.buy()
        else:
            if self.dataclose[0] < self.dataclose[-1]:
                self.order = self.sell()


def show_backtest():

    with st.expander("Useful links", expanded=False):
        st.write("Investopedia  [7 Technical Indicators to Build a Trading Toolkit](https://www.investopedia.com/top-7-technical-analysis-tools-4773275)")
        st.write(
            "Investopedia   [5 Must-Have Metrics for Value Investors](https://www.investopedia.com/articles/fundamental-analysis/09/five-must-have-metrics-value-investors.asp)")

    st.subheader('Backtrader Integration')
    with st.expander("Specify Entry strategy", expanded=False):
        st.text("Dummy entry strategy")
    with st.expander("Specify Exit strategy", expanded=False):
        st.text("Dummy exit strategy")
    # Choose a ticker
    ticker = st.text_input("Enter a Ticker", 'AAPL')

    if st.button('Run backtest'):
        data = yf.download(ticker, start='2020-01-01', end='2021-12-31')

        # Insert your code here to add your custom fundamental/technical data to the dataframe.
        # Note: For the purposes of this demo, random data is used.
        data['price_to_earning'] = np.random.random(size=len(data))
        # ... Add other columns in the same way

        # Pass it to the backtrader datafeed and add it to the cerebro
        data_feed = ExtendedPandasData(dataname=data)
        cerebro = bt.Cerebro()
        cerebro.adddata(data_feed)
        cerebro.addstrategy(TestStrategy)
        cerebro.run()
        cerebro.plot()

        # Display the data
        st.write(data)
