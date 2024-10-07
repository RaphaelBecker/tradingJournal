import streamlit as st
import yfinance as yf
import backtrader as bt
from backtrader.feeds import PandasData
import numpy as np
import datetime
import importlib
import os

strategies_dict = {}

# Define the directory where your strategy files are located
directory = 'strategies'

# Iterate over all Python files in the directory
for filename in os.listdir(directory):
    if filename.endswith('.py'):
        # Remove the .py part to get the module name
        module_name = filename[:-3]
        # Import the module
        module = importlib.import_module(f'{directory}.{module_name}')
        # Assume each file only has one class, get that class
        # Note: This will only get the first class in each file
        strategy_class = next(c for n, c in module.__dict__.items() if isinstance(c, type))
        # Add the class to the dictionary
        strategies_dict[module_name] = strategy_class

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
        st.write(
            "Research       [Yahoo Ticker Research](https://finance.yahoo.com/lookup)")


    col1, col2, col3, col4 = st.columns(4)
    with col1:
        # Choose a ticker
        ticker_list = st.selectbox("Choose ticker list", ["Manual selection", "Watchlist", "Open Trades"])
        ticker = "APPL"
        if ticker_list == "Manual selection":
            ticker = st.text_input("Choose Ticker", 'AAPL')
        if ticker_list == "Watchlist":
            ticker = st.selectbox("Chosse from Watchlist", ["APPL", "TSLA", "NFLX", "S92.DE"])
        if ticker_list == "Open Trades":
            ticker = st.selectbox("Chosse from Open Trades", ["APPL", "TSLA", "NFLX"])
    with col2:
        start_date = st.date_input("Start Date", value=datetime.date(2021,1, 1))
        strategy_chosen = st.selectbox("Select Strategy", strategies_dict.keys())
    with col3:
        end_date = st.date_input("End Date")
        stake = int(st.text_input("Set trade stake", value=5))
    with col4:
        cash = int(st.text_input("Set start cash", value=1000))
        comission = float(st.text_input("Comission [%]", value=0.1))
    st.subheader('Backtrader Integration')


    OHLC_dataframe = None
    info_dict = None

    button_col1, button_col2, _3, _4, _5, _6, _7 = st.columns(7)

    with button_col1:
        if st.button("Show API Ticker Data"):
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
        data1 = cerebro.resampledata(data_feed, timeframe=bt.TimeFrame.Months, compression=1)
        data1.plotinfo.plot = False

        # set cash
        cerebro.broker.setcash(cash=cash)
        # Add a FixedSize sizer according to the stake
        cerebro.addsizer(bt.sizers.FixedSize, stake=stake)

        # 0.1% ... divide by 100 to remove the %
        cerebro.broker.setcommission(commission=(comission/100))

        # Add the analyzer to the Cerebro engine
        cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name="tradeanalyzer")

        # RUN
        # Print out the starting conditions
        start_cash = cerebro.broker.getvalue()
        results = cerebro.run()
        strat = results[0]
        protfolio_value = cerebro.broker.getvalue()
        account_cash = cerebro.broker.getcash()
        backtested_days = end_date - start_date

        try:
            print('\n# Stats: -----------------------------------------------------------')
            print('Starting Portfolio Value: %.2f' % start_cash)
            # Print out the final result
            print('Final Portfolio Value: %.2f' % protfolio_value)
            print('Remaining Cash: %.2f' % account_cash)
            print('Gain: %.2f' % (protfolio_value + account_cash - start_cash))
            print("Total trades:", strat.analyzers.tradeanalyzer.get_analysis().total.closed)
            print("Total wins:", strat.analyzers.tradeanalyzer.get_analysis().won.total)
            print("Total losses:", strat.analyzers.tradeanalyzer.get_analysis().lost.total)
            # calculate the win rate
            win_rate = strat.analyzers.tradeanalyzer.get_analysis().won.total / strat.analyzers.tradeanalyzer.get_analysis().total.closed
            print('Win Rate: %.2f%%' % (win_rate * 100))
            print(f'Backtested days: {backtested_days.days}')
            print('# -------------------------------------------------------------------\n')
        except KeyError as e:
            print(f"Keyerror: {e}")

        cerebro.plot(start=start_date, end=end_date,
        #  Format string for the display of ticks on the x axis
        fmt_x_ticks = '%Y-%b-%d %H:%M',
        # Format string for the display of data points values
        fmt_x_data = '%Y-%b-%d %H:%M', style='candlestick', barup='green', bardown='red')

        # Display the data
        st.write(OHLC_dataframe)



