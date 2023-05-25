import streamlit as st
import pandas as pd
import os
import pathlib
import data_specs
import matplotlib.pyplot as plt
from datetime import datetime



ROOT_DIR = pathlib.Path(__file__).resolve().parents[0]
filepath_datastore = ROOT_DIR.joinpath('local_storage').joinpath('trades.csv')
filepath_selected_cols = ROOT_DIR.joinpath('local_storage').joinpath('selected_columns.txt')
st.set_page_config(layout="wide")

if 'page' not in st.session_state:
    st.session_state.page = 'Dashboard'

if 'title' not in st.session_state:
    st.session_state.title = "DASHBOARD"

if 'metric1' not in st.session_state:
    st.session_state.metric1 = "tradeinfo_entry_price"

if 'additional_metrics' not in st.session_state:
    st.session_state.additional_metrics = ""

# https://www.investopedia.com/top-7-technical-analysis-tools-4773275
# https://www.investopedia.com/articles/fundamental-analysis/09/five-must-have-metrics-value-investors.asp

def load_data():
    if os.path.exists(filepath_datastore):
        df = pd.read_csv(filepath_datastore)
        # Convert exit dates to datetime if not already
        df['tradeinfo_entry_date'] = pd.to_datetime(df['tradeinfo_entry_date'])
        df['tradeinfo_exit_date'] = pd.to_datetime(df['tradeinfo_exit_date'])

        return df
    else:
        return pd.DataFrame(columns=data_specs.journal_data_df_colums)


def save_data(df):
    df = df.sort_values(by="tradeinfo_entry_date", ascending=False)
    df.to_csv(filepath_datastore, index=False)

def save_selected_columns(columns):
    with open(filepath_selected_cols, 'w') as f:
        for column in columns:
            f.write(column + '\n')

def load_selected_columns():
    try:
        with open(filepath_selected_cols, 'r') as f:
            return [line.strip() for line in f.readlines()]
    except FileNotFoundError:
        st.error(f"selected_columns in {filepath_selected_cols} not found")
        return []

def color_negative_red_positive_green(val):
    try:
        val = float(val)
        color = 'red' if val < 0 else 'green' if val > 0 else 'black'
    except ValueError:
        color = 'black'  # Default color for non-numeric data
    return f'color: {color}'

# Function to categorize columns
def categorize_column(col_name):
    if "tradeinfo" in col_name:
        return 0
    elif "fundamentals" in col_name:
        return 1
    elif "technical" in col_name:
        return 2
    elif "human" in col_name:
        return 3
    else:
        return -1

def get_label(labelstring):
    return " ".join(labelstring.split("_")[1:])


def main():

    column1, column2, column3, _4, _5, _6, _7 = st.columns(7)
    with column1:
        if st.button('Dashboard'):
            st.session_state.page = "Dashboard"
            st.session_state.title = "DASHBOARD"

    with column2:
        if st.button('Manage Trades'):
            st.session_state.page = "Manage Trades"
            st.session_state.title = "MANAGE TRADES"

    with column3:
        if st.button('Analysis'):
            st.session_state.page = "Analysis"
            st.session_state.title = "ANALYISIS"


    st.title(st.session_state.title)

    df = load_data()

    if st.session_state.page == "Dashboard":
        df = show_dashboard(df)
    elif st.session_state.page == "Manage Trades":
        df = show_manage_trades(df)
    elif st.session_state.page == "Analysis":
        df = show_analysis(df)

    save_data(df)


def show_dashboard(df):
    # Calculate some basic statistics
    total_trades = df.shape[0]
    winning_trades = df[df['tradeinfo_gain_absolut'] > 0].shape[0]
    losing_trades = df[df['tradeinfo_gain_absolut'] < 0].shape[0]
    win_rate = winning_trades / total_trades

    average_win = df[df['tradeinfo_gain_absolut'] > 0]['tradeinfo_gain_absolut'].mean()
    average_loss = df[df['tradeinfo_gain_absolut'] < 0]['tradeinfo_gain_absolut'].mean()

    #---------------------------------------------------------------------------------------------------------------

    # Calculate the total profit from winning trades
    total_profit = df[df['tradeinfo_gain_absolut'] > 0]['tradeinfo_gain_absolut'].sum()

    # Calculate the total loss from losing trades
    # Since losses are represented as negative numbers, we need to multiply by -1 to get a positive total loss
    total_loss = (-1) * df[df['tradeinfo_gain_absolut'] < 0]['tradeinfo_gain_absolut'].sum()

    #---------------------------------------------------------------------------------------------------------------

    # Calculate the Profit Factor
    profit_factor = round(total_profit / total_loss, 2)

    # Calculate the cumulative returns
    cumulative_returns = df['tradeinfo_gain_absolut'].cumsum()

    # Calculate the running maximum
    running_max = cumulative_returns.cummax()

    # Calculate the drawdown
    drawdown = running_max - cumulative_returns

    # Maximum drawdown in dollar terms
    max_drawdown_value = round(drawdown.max(),2)

    # Maximum drawdown as a percentage of the portfolio value
    max_drawdown_percentage = round(drawdown.max() / running_max.max(), 2)

    #---------------------------------------------------------------------------------------------------------------

    st.subheader("BASIC TRADING STATISTICS")
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    with col1:
        st.metric("Total number of trades", total_trades)
    with col2:
        st.metric("Number of winning trades", winning_trades)
    with col3:
        st.metric("Number of losing trades", losing_trades)
    with col4:
        st.metric("Win rate [%]", f"{win_rate * 100:.2f}")
    with col5:
        st.metric("Average win [EUR]", f"{average_win:.2f}")
    with col6:
        st.metric("Average loss [EUR]", f"{average_loss:.2f}")



    # Add placeholder for other metrics
    with col1:
        st.metric("Profit Factor", profit_factor)
    with col2:
        st.metric("Max Drawdown", max_drawdown_value)
    with col3:
        st.metric("Max Drawdown [%]", max_drawdown_percentage)

    # -------------------------------------------------------------------------------------------------------------
    # PLOT GAIN:
    st.subheader("ACCUMULATED GAIN")
    # Ensure 'tradeinfo_exit_date' is in datetime format
    df['tradeinfo_exit_date'] = pd.to_datetime(df['tradeinfo_exit_date'])

    # Ensure 'tradeinfo_gain_absolut' is numeric (float or int)
    df['tradeinfo_gain_absolut'] = pd.to_numeric(df['tradeinfo_gain_absolut'], errors='coerce')

    # Sort dataframe by 'tradeinfo_exit_date'
    df = df.sort_values('tradeinfo_exit_date')

    # Compute accumulated gain
    df['accumulated_gain'] = df['tradeinfo_gain_absolut'].cumsum()

    # Plot
    st.area_chart(df.set_index('tradeinfo_exit_date')['accumulated_gain'])

    # -------------------------------------------------------------------------------------------------------------
    # PLOT ADDITIONAL METRICS:
    st.subheader("COMPARE METRICS")
    # List of metrics available for plotting
    metrics = ['tradeinfo_entry_price', 'tradeinfo_exit_price', 'tradeinfo_gain_percentage',
               'tradeinfo_gain_absolut', 'tradeinfo_tax', 'tradeinfo_fees', 'fundamentals_market_cap',
               'fundamentals_price_to_earning', 'fundamentals_price_to_book', 'fundamentals_dept_to_equity',
               'fundamentals_free_cash_flow', 'fundamentals_PEG_ratio', 'technical_RSI', 'technical_trend_mac_d',
               'technical_on_balance_volume', 'technical_AD_line', 'technical_ADX', 'technical_aroon_indicator']

    metric_col1, metric_col2 = st.columns(2)
    with metric_col1:
        st.session_state.metric1 = st.selectbox('Select metric 1:', options=metrics)
    with metric_col2:
        st.session_state.additional_metrics = st.multiselect('Select additional metrics:', options=metrics)

    # Combine metric1 and additional metrics
    selected_metrics = [st.session_state.metric1] + st.session_state.additional_metrics

    # Plot
    st.line_chart(df.set_index('tradeinfo_exit_date')[selected_metrics])


    return df


def show_manage_trades(df):
    with st.expander("Add new trade"):
        with st.form(key='new_trade_form'):
            st.header('Add a New Trade')
            new_trade_data = {}

            cols = st.columns(4)
            for col in df.columns:
                # Categorize the column
                category = categorize_column(col)

                # If the column belongs to one of the categories, create a text input for it in the corresponding column
                if category >= 0:
                    label = " ".join(col.split("_")[1:])
                    if "sector" in label:
                        new_trade_data[col] = cols[category].selectbox(f"{label}", data_specs.sectors)
                    if "market cap" in label:
                        new_trade_data[col] = cols[category].selectbox(f"{label}", data_specs.market_cap_ranges)
                    if "date" in label:
                        new_trade_data[col] = cols[category].date_input(f"{label}", datetime.now())
                    else:
                        new_trade_data[col] = cols[category].text_input(f"{label}")

            submit_button = st.form_submit_button(label='Submit New Trade')

            if submit_button:
                # Append the new trade to the DataFrame
                df.loc[len(df)] = new_trade_data
                st.success('New trade added successfully!')

    with st.expander("Edit trade"):
        # Let the user select a trade to edit
        trade_to_edit = st.selectbox('Select a trade to edit', df.index)

        # Create the form to edit the selected trade
        with st.form(key='edit_trade_form'):
            st.header(f'Edit Trade {trade_to_edit}')
            edit_trade_data = {}

            # Create 4 columns
            cols = st.columns(4)

            for col in df.columns:
                # Categorize the column
                category = categorize_column(col)
                default_value = df.loc[trade_to_edit, col]

                # If the column belongs to one of the categories, create a text input for it in the corresponding column
                if category >= 0:
                    label = " ".join(col.split("_")[1:])
                    edit_trade_data[col] = cols[category].text_input(f"{label}",
                                                                     value=default_value)

            # Create submit and delete buttons in a row
            cols = st.columns(2)
            submit_button = cols[0].form_submit_button(label='Submit Changes')
            delete_button = cols[1].form_submit_button('Delete Trade')

            if submit_button:
                # Update the trade in the DataFrame
                for col in df.columns:
                    df.loc[trade_to_edit, col] = edit_trade_data[col]
                st.success(f'Trade {trade_to_edit} updated successfully!')

            if delete_button:
                # Delete the trade from the DataFrame
                df = df.drop(trade_to_edit)
                st.success(f'Trade {trade_to_edit} deleted successfully!')


    default_columns = load_selected_columns()
    #default_columns = [get_label(label) for label in default_columns]
    #st.text(default_columns)
    selected_columns = st.multiselect("Select the columns you want to display", df.columns, default=default_columns)

    col1, col2, col3, col4 = st.columns(4)

    if selected_columns:
        sort_options = ["None"] + df.columns.tolist()
        with col1:
            sort_column = st.selectbox("Select column to sort by", sort_options)
        with col2:
            ascending = st.checkbox("iverse sorting")

        if sort_column != "None":
            df = df.sort_values(sort_column, ascending=ascending)
        # Create a list of all columns in selected_columns containing 'gain'
        gain_columns = [s for s in selected_columns if "gain" in s]

        if gain_columns:
            styled_df = df[selected_columns].style.applymap(color_negative_red_positive_green, subset=gain_columns)
            st.markdown(styled_df.to_html(escape=False), unsafe_allow_html=True)
        else:
            st.experimental_data_editor(df[selected_columns])
        save_selected_columns(selected_columns)
    else:
        st.write("Select columns from selectbox!")

    return df


def show_analysis(df):
    return df


if __name__ == "__main__":
    main()
