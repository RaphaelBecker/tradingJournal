import streamlit as st
import yfinance as yf
import backtrader as bt
from backtrader.feeds import PandasData
import numpy as np
import datetime
from backtest_strategies import BuyAndHold
from backtest_strategies import TDI

strategies_dict = {
    "TDI": TDI,
    "Buy and Hold": BuyAndHold,
}

@st.cache_data  # cache
def load_OHLC(ticker, start_date, end_date):
    data = yf.download(ticker, start=start_date, end=end_date)
    return data

@st.cache_data  # cache
def load_INFO(ticker):
    return yf.Ticker(ticker).info

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


def show_backtest():

    with st.expander("Useful links", expanded=False):
        st.write("Investopedia  [7 Technical Indicators to Build a Trading Toolkit](https://www.investopedia.com/top-7-technical-analysis-tools-4773275)")
        st.write(
            "Investopedia   [5 Must-Have Metrics for Value Investors](https://www.investopedia.com/articles/fundamental-analysis/09/five-must-have-metrics-value-investors.asp)")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        # Choose a ticker
        ticker = st.text_input("Choose Ticker", 'AAPL')
        strategy_chosen = st.selectbox("Select Strategy", strategies_dict.keys())
    with col2:
        start_date = st.date_input("Start Date", value=datetime.date(2021,1, 1))

    with col3:
        end_date = st.date_input("End Date")
        stake = int(st.text_input("Set trade stake", value=5))
    with col4:
        cash = int(st.text_input("Set start cash", value=1000))
        comission = float(st.text_input("Comission [%]", value=0.1))
    st.subheader('Backtrader Integration')


    OHLC_dataframe = None
    info_dict = None

    button_col1, button_col2, _3, _4 = st.columns(4)

    with button_col1:
        if st.button("Show API Ticket Data"):
            info_dict = load_INFO(ticker)
    with button_col2:
        if st.button('Run backtest'):
            OHLC_dataframe = load_OHLC(ticker=ticker, start_date=start_date, end_date=end_date)


    if info_dict:
        st.write(info_dict)


    if OHLC_dataframe is not None:
        cerebro = bt.Cerebro()

        # Add combined strategy to cerebro
        cerebro.addstrategy(strategies_dict[strategy_chosen])

        # Pass it to the backtrader datafeed and add it to the cerebro
        data_feed = ExtendedPandasData(dataname=OHLC_dataframe)
        cerebro.adddata(data_feed)
        # Add resampled data for Pivot Indicator resampled data: data1
        cerebro.resampledata(data_feed, timeframe=bt.TimeFrame.Months)

        # set cash
        cerebro.broker.setcash(cash=cash)
        # Add a FixedSize sizer according to the stake
        cerebro.addsizer(bt.sizers.FixedSize, stake=stake)

        # 0.1% ... divide by 100 to remove the %
        cerebro.broker.setcommission(commission=(comission/100))

        # RUN
        # Print out the starting conditions
        print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
        cerebro.run()
        # Print out the final result
        print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

        cerebro.plot(start=start_date, end=end_date,
        #  Format string for the display of ticks on the x axis
        fmt_x_ticks = '%Y-%b-%d %H:%M',
        # Format string for the display of data points values
        fmt_x_data = '%Y-%b-%d %H:%M')

        # Display the data
        st.write(OHLC_dataframe)



