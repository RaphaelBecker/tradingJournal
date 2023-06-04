import streamlit as st
import pandas as pd
import os
import pathlib
import data_specs
import matplotlib.pyplot as plt
from collections.abc import Iterable
from datetime import datetime
from PIL import Image
import io
import tempfile
import backtest
import numpy as np
import seaborn as sns
import calendar
from matplotlib.colors import ListedColormap
import itertools

# state and paths
ROOT_DIR = pathlib.Path(__file__).resolve().parents[0]
filepath_datastore = ROOT_DIR.joinpath('local_storage').joinpath('trades.csv')
filepath_selected_cols = ROOT_DIR.joinpath('local_storage').joinpath('selected_columns.txt')
st.set_page_config(layout="wide")

# Set pandas to display float format to remove trailing zeros
pd.options.display.float_format = '{:,.2f}'.format

if 'page' not in st.session_state:
    st.session_state.page = 'Dashboard'

if 'title' not in st.session_state:
    st.session_state.title = "DASHBOARD"

if 'metric1' not in st.session_state:
    st.session_state.metric1 = "tradeinfo_entry_price"

if 'metric2' not in st.session_state:
    st.session_state.metric2 = "human_mood_on_entry"

if 'additional_metrics' not in st.session_state:
    st.session_state.additional_metrics = ""

# https://www.investopedia.com/top-7-technical-analysis-tools-4773275
# https://www.investopedia.com/articles/fundamental-analysis/09/five-must-have-metrics-value-investors.asp

def load_data():
    if os.path.exists(filepath_datastore):
        df = pd.read_csv(filepath_datastore)
        # Convert exit dates to datetime if not already
        df['tradeinfo_entry_date'] = pd.to_datetime(df['tradeinfo_entry_date'], format="%Y-%m-%d")
        df['tradeinfo_exit_date'] = pd.to_datetime(df['tradeinfo_exit_date'], format="%Y-%m-%d")
        print(f"loaded dataframe: {len(df)}")
        return df
    else:
        return pd.DataFrame(columns=data_specs.journal_data_df_colums)


def save_data(df):
    # Ensure 'tradeinfo_entry_date' is in datetime format
    df['tradeinfo_entry_date'] = pd.to_datetime(df['tradeinfo_entry_date'], format="%Y-%m-%d %H:%M:%S")
    df['tradeinfo_exit_date'] = pd.to_datetime(df['tradeinfo_exit_date'], format="%Y-%m-%d %H:%M:%S")
    df = df.sort_values(by="tradeinfo_entry_date", ascending=False)
    df.to_csv(filepath_datastore, index=False)
    print(f"saved dataframe: {len(df)}")

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
    color = 'red' if val < 1 else 'green' if val > 1 else 'white'
    return f'background-color: {color}'


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
        if st.button('Analyse Strategy'):
            st.session_state.page = "Analysis"
            st.session_state.title = "STRATEGY ANALYISIS"


    st.title(st.session_state.title)

    df = load_data()

    #-----------------------------------------------------------------------------------------------------------------
    # Calculate gains when all prices are given:
    # Ensure 'tradeinfo_entry_price', 'tradeinfo_exit_price' and 'tradeinfo_number_shares' are in float format
    df['tradeinfo_entry_price'] = pd.to_numeric(df['tradeinfo_entry_price'], errors='coerce')
    df['tradeinfo_exit_price'] = pd.to_numeric(df['tradeinfo_exit_price'], errors='coerce')
    df['tradeinfo_number_shares'] = pd.to_numeric(df['tradeinfo_number_shares'], errors='coerce')

    # Save rows with null 'tradeinfo_entry_price', 'tradeinfo_exit_price' or 'tradeinfo_number_shares'
    buffer_df = df[df['tradeinfo_entry_price'].isnull() | df['tradeinfo_exit_price'].isnull() | df[
        'tradeinfo_number_shares'].isnull()]

    # Filter the dataframe to only include rows where 'tradeinfo_entry_price', 'tradeinfo_exit_price' and 'tradeinfo_number_shares' are not null
    df = df[df['tradeinfo_entry_price'].notnull() & df['tradeinfo_exit_price'].notnull() & df[
        'tradeinfo_number_shares'].notnull()]

    # Calculate 'tradeinfo_gain_absolut'
    df['tradeinfo_gain_absolut'] = (df['tradeinfo_exit_price'] - df['tradeinfo_entry_price']) * df[
        'tradeinfo_number_shares']

    # Calculate 'tradeinfo_gain_percentage'
    df['tradeinfo_gain_percentage'] = ((df['tradeinfo_exit_price'] / df['tradeinfo_entry_price']) - 1) * 100

    # Append the buffered rows back to the DataFrame
    df = pd.concat([df, buffer_df], ignore_index=True)
    # -----------------------------------------------------------------------------------------------------------------

    # Round all columns in the DataFrame

    # Financial figures are typically rounded to 2 decimal places
    df[['tradeinfo_entry_price', 'tradeinfo_exit_price', 'tradeinfo_fees', 'tradeinfo_tax', 'tradeinfo_gain_absolut',
        'fundamentals_market_cap', 'fundamentals_free_cash_flow']] = df[['tradeinfo_entry_price',
        'tradeinfo_exit_price', 'tradeinfo_fees', 'tradeinfo_tax', 'tradeinfo_gain_absolut', 'fundamentals_market_cap',
                                              'fundamentals_free_cash_flow']].round(2)

    # Percentages are typically rounded to 2 decimal places
    df[['tradeinfo_gain_percentage', 'technical_RSI']] = df[['tradeinfo_gain_percentage', 'technical_RSI']].round(2)

    # Ratios are typically rounded to 2 decimal places
    df[['fundamentals_price_to_earning', 'fundamentals_price_to_book', 'fundamentals_dept_to_equity',
        'fundamentals_PEG_ratio', 'technical_trend_mac_d', 'technical_on_balance_volume',
        'technical_AD_line', 'technical_ADX', 'technical_aroon_indicator']] = df[['fundamentals_price_to_earning',
                                                                                  'fundamentals_price_to_book',
                                                                                  'fundamentals_dept_to_equity',
                                                                                  'fundamentals_PEG_ratio',
                                                                                  'technical_trend_mac_d',
                                                                                  'technical_on_balance_volume',
                                                                                  'technical_AD_line', 'technical_ADX',
                                                                                  'technical_aroon_indicator']].round(2)

    # -----------------------------------------------------------------------------------------------------------------

    if st.session_state.page == "Dashboard":
        show_dashboard(df)
    elif st.session_state.page == "Manage Trades":
        show_manage_trades(df)
    elif st.session_state.page == "Analysis":
        show_analysis(df)


def show_dashboard(df):
    if len(df)>0:
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

        # Ensure 'tradeinfo_entry_date' and 'tradeinfo_exit_date' are in datetime format
        df['tradeinfo_entry_date'] = pd.to_datetime(df['tradeinfo_entry_date'])
        df['tradeinfo_exit_date'] = pd.to_datetime(df['tradeinfo_exit_date'])

        # Filter the dataframe to only include rows where 'tradeinfo_exit_date' is not null
        df_tradeinfo_exit_date = df[df['tradeinfo_exit_date'].notnull()]

        # Calculate holding period for each trade
        holding_period = df_tradeinfo_exit_date['tradeinfo_exit_date'] - df_tradeinfo_exit_date['tradeinfo_entry_date']

        # Calculate average holding period
        average_holding_period = holding_period.mean()

        # ---------------------------------------------------------------------------------------------------------------

        st.subheader("BASIC TRADING STATISTICS")
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        with col1:
            st.metric("Total number of trades", total_trades)
        with col2:
            st.metric("Win / Loose", f"{winning_trades} / {losing_trades}")
        with col3:
            st.metric("Win rate [%]", f"{win_rate * 100:.2f}")
        with col4:
            st.metric("Average win [EUR]", f"{average_win:.2f}")
        with col5:
            st.metric("Average loss [EUR]", f"{average_loss:.2f}")



        # Add placeholder for other metrics
        with col1:
            st.metric("Profit Factor", profit_factor)
        with col2:
            st.metric("Max Drawdown", max_drawdown_value)
        with col3:
            st.metric("Max Drawdown [%]", max_drawdown_percentage)
        with col4:
            st.metric("Average holding period [days]", str(average_holding_period.days))

        # -------------------------------------------------------------------------------------------------------------
        # PLOT GAIN:
        st.subheader("ACCUMULATED GAIN")
        # Ensure 'tradeinfo_exit_date' is in datetime format
        df['tradeinfo_exit_date'] = pd.to_datetime(df['tradeinfo_exit_date'])

        # Ensure 'tradeinfo_gain_absolut' is numeric (float or int)
        df['tradeinfo_gain_absolut'] = pd.to_numeric(df['tradeinfo_gain_absolut'], errors='coerce')

        # Sort dataframe by 'tradeinfo_exit_date'
        df_acc_gain = df.sort_values('tradeinfo_exit_date')

        # Compute accumulated gain
        df_acc_gain['accumulated_gain'] = df_acc_gain['tradeinfo_gain_absolut'].cumsum()

        # Plot
        st.area_chart(df_acc_gain.set_index('tradeinfo_exit_date')['accumulated_gain'])

        # -------------------------------------------------------------------------------------------------------------
        # PLOT ADDITIONAL METRICS:
        st.subheader("COMPARE METRICS")
        # List of metrics available for plotting
        metrics = ['tradeinfo_entry_price', 'tradeinfo_exit_price', 'tradeinfo_gain_percentage',
                   'tradeinfo_gain_absolut', 'tradeinfo_tax', 'tradeinfo_fees', 'fundamentals_market_cap',
                   'fundamentals_price_to_earning', 'fundamentals_price_to_book', 'fundamentals_dept_to_equity',
                   'fundamentals_free_cash_flow', 'fundamentals_PEG_ratio', 'technical_RSI', 'technical_trend_mac_d',
                   'technical_on_balance_volume', 'technical_AD_line', 'technical_ADX', 'technical_aroon_indicator']

        metrics2 = ["human_trading_idea_description", "human_mood_on_entry", "human_mood_on_exit", "human_mistake",
                   "human_reflection_for_improvement"]

        metric_col1, metric_col2 = st.columns(2)
        with metric_col1:
            st.session_state.metric1 = st.selectbox('Select metric 1:', options=metrics)
        with metric_col2:
            st.session_state.additional_metrics = st.multiselect('Select additional metrics:', options=metrics)

        # Combine metric1 and additional metrics
        selected_metrics = [st.session_state.metric1] + st.session_state.additional_metrics

        # Plot
        st.line_chart(df.set_index('tradeinfo_exit_date')[selected_metrics])

        # second plot for comparing different units
        st.session_state.metric2 = st.selectbox('Select metric 2:', options=metrics2)
        # Sort DataFrame by date
        df_sorted = df.sort_values('tradeinfo_exit_date')

        # Plot
        counts = df[st.session_state.metric2].value_counts()
        st.bar_chart(counts)

    #-----------------------------------------------------------------------------------------------------------------
        # Plot proftable days and negative days in a heatmap:

        st.subheader("CALENDAR VIEW:")
        # Parse dates and sort by date
        df_temp = df.copy()  # create a copy of df to avoid changing it
        df_temp["tradeinfo_exit_date"] = pd.to_datetime(df_temp["tradeinfo_exit_date"])
        df_temp.sort_values(by="tradeinfo_exit_date", inplace=True)

        # Create a column for the year
        df_temp["year"] = df_temp["tradeinfo_exit_date"].dt.year

        # Get unique years and create dropdown menu
        unique_years = df_temp["year"].unique()
        selected_year = st.selectbox("Select a Year", unique_years)

        # Filter the DataFrame based on the selected year
        df_temp = df_temp[df_temp["year"] == selected_year]

        # Resample by day and calculate sum of gains
        df_daily = df_temp.groupby(["tradeinfo_exit_date"])["tradeinfo_gain_percentage"].sum().reset_index()

        # Fill the missing dates with 0 gain
        all_dates = pd.date_range(start=df_daily["tradeinfo_exit_date"].min(),
                                  end=df_daily["tradeinfo_exit_date"].max())
        df_daily.set_index("tradeinfo_exit_date", inplace=True)
        df_daily = df_daily.reindex(all_dates, fill_value=0).reset_index().rename(
            columns={"index": "tradeinfo_exit_date"})

        # Add separate columns for day and month
        df_daily["day"] = df_daily["tradeinfo_exit_date"].dt.day
        df_daily["month"] = df_daily["tradeinfo_exit_date"].dt.month

        # Aggregate by month and day before pivoting
        if 'tradeinfo_exit_date' in df_daily.columns:
            df_daily = df_daily.drop(columns=['tradeinfo_exit_date'])

        # Ensure to sum only on 'tradeinfo_gain_percentage'
        df_daily = df_daily.groupby(["month", "day"])['tradeinfo_gain_percentage'].sum().reset_index()

        # Add this before pivoting
        df_daily = df_daily.groupby(["month", "day"])['tradeinfo_gain_percentage'].sum().reset_index()

        # Create a new DataFrame with a complete list of days for each month
        all_months_days = pd.DataFrame(list(itertools.product(range(1, 13), range(1, 32))), columns=['month', 'day'])

        # Merge this with the original DataFrame, filling missing values with 0
        df_daily = pd.merge(all_months_days, df_daily, how='left', on=['month', 'day'])
        df_daily['tradeinfo_gain_percentage'].fillna(0, inplace=True)

        # Now you can pivot the DataFrame as before
        df_pivot = df_daily.pivot(index="day", columns="month", values="tradeinfo_gain_percentage")

        # Create a custom colormap
        cmap = ListedColormap(['red', 'white', 'green'])

        # Create a 3x4 grid of subplots
        fig, axes = plt.subplots(3, 4, figsize=(15, 10))

        for i, ax in enumerate(axes.flatten()):
            # Create the heatmap
            sns.heatmap(df_pivot.iloc[:, [i]], cmap=cmap, ax=ax)

            # Set the title to the month name
            ax.set_title(calendar.month_name[i + 1])

        # Remove empty subplots
        if df_pivot.shape[1] < 12:
            for j in range(df_pivot.shape[1], 12):
                fig.delaxes(axes.flatten()[j])

        plt.tight_layout()
        plt.show()

        # Use streamlit to display the figure
        st.pyplot(fig)


    else:
        st.info("Your trading list is empty! In order to add trades, go to Manage Trades.")



def show_manage_trades(df):
    with st.expander("Open new trade"):
        with st.form(key='new_trade_form'):
            st.header('Open Trade')

            open_trade_data = {}
            uploaded_file_path = None
            uploaded_file = st.file_uploader("Upload an image")

            if uploaded_file is not None:
                # Create the images directory if it doesn't already exist
                images_dir = ROOT_DIR.joinpath('local_storage').joinpath('images')
                images_dir.mkdir(parents=True, exist_ok=True)

                # Save the uploaded file to the images directory
                uploaded_file_path = images_dir.joinpath(uploaded_file.name)
                with open(uploaded_file_path, 'wb') as out_file:
                    out_file.write(uploaded_file.read())

                st.success(f"Image saved to {uploaded_file_path}")

            cols = st.columns(4)
            for col in df.columns:
                # Categorize the column
                category = categorize_column(col)

                # If the column belongs to one of the categories, create a text input for it in the corresponding column
                if category >= 0:
                    label = " ".join(col.split("_")[1:])
                    if "sector" in label:
                        open_trade_data[col] = cols[category].selectbox(f"{label}", data_specs.sectors)
                    elif "market cap" in label:
                        open_trade_data[col] = cols[category].selectbox(f"{label}", data_specs.market_cap_ranges)
                    elif "risk reward ratio" in label:
                        open_trade_data[col] = cols[category].selectbox(f"{label}", data_specs.risk_reward_ratios)
                    elif "market sentiment" in label:
                        open_trade_data[col] = cols[category].selectbox(f"{label}", data_specs.market_sentiment)
                    elif "analyst rating" in label:
                        open_trade_data[col] = cols[category].selectbox(f"{label}", data_specs.analyst_ratings)
                    elif "mood on entry" in label:
                        open_trade_data[col] = cols[category].selectbox(f"{label}", data_specs.sorted_moods)
                    elif "entry date" in label:
                        open_trade_data[col] = cols[category].date_input(f"{label}", datetime.now())
                    elif "picture path" in label:
                        open_trade_data[col] = str(uploaded_file_path)
                    else:
                        close_trade_labels = ["mood on exit", "mistake", "reflection for", "exit date", "exit price", "tax", "fees", "gain"]
                        if not any(close_trade_label in label for close_trade_label in close_trade_labels):
                            open_trade_data[col] = cols[category].text_input(f"{label}")
                        else:
                            open_trade_data[col] = None

            open_button = st.form_submit_button(label='Open Trade')

            if open_button:
                # Append the new trade to the DataFrame
                df.loc[len(df)] = open_trade_data
                save_data(df)
                st.success('Trade opened successfully!')

    with st.expander("Close Trade"):
        # Let the user select a trade to edit
        # Filter DataFrame where 'tradeinfo_exit_price' is NaN
        open_trades = df[df['tradeinfo_exit_price'].isna()]

        # open_trades = ensure_iterable(open_trades.index)

        # Use the filtered DataFrame in the selectbox
        trade_to_close = st.selectbox('Select a trade to close', open_trades.index)

        # Create the form to edit the selected trade
        if trade_to_close is not None:
            with st.form(key='close_trade_form'):
                st.header(f'Close Trade {trade_to_close}')
                close_trade_data = {}

                image_path = None
                if df.loc[trade_to_close, "human_picture_path"]:
                    image_path = pathlib.Path(str(df.loc[trade_to_close, "human_picture_path"]))

                # Check if the path is valid
                if image_path is not None:
                    try:
                        image = Image.open(image_path)
                        st.image(image, caption='Uploaded Image', width=800)
                    except IOError as e:
                        st.write(f"IMAGE: Could not read file, does it exist?..  {image_path}: {e}")
                else:
                    st.write("IMAGE: The image file does not exist.")


                # Create 4 columns
                cols = st.columns(4)

                for col in df.columns:
                    # Categorize the column
                    category = categorize_column(col)
                    default_value = df.loc[trade_to_close, col]

                    # If the column belongs to one of the categories, create a text input for it in the corresponding column
                    if category >= 0:
                        label = " ".join(col.split("_")[1:])
                        if "Ticker" in label:
                            close_trade_data[col] = cols[category].text_input(f"{label}",default_value)
                        if "entry date" in label:
                            close_trade_data[col] = cols[category].date_input(f"{label}",default_value)
                        elif "mood on exit" in label:
                            close_trade_data[col] = cols[category].selectbox(f"{label}",
                                                                             data_specs.sorted_moods)
                        elif "mistake" in label:
                            close_trade_data[col] = cols[category].selectbox(f"{label}",
                                                                            data_specs.trading_mistakes)
                        elif "exit date" in label:
                            close_trade_data[col] = cols[category].date_input(f"{label}", datetime.now())
                        else:
                            close_trade_labels = ["reflection for", "exit price", "entry price"]
                            if any(close_trade_label in label for close_trade_label in close_trade_labels):
                                close_trade_data[col] = cols[category].text_input(f"{label}", default_value)
                            else:
                                close_trade_data[col] = default_value

                close_button = st.form_submit_button(label='Close Trade')

                if close_button:
                    # Update the trade in the DataFrame
                    for col in df.columns:
                        df.loc[trade_to_close, col] = close_trade_data[col]
                    save_data(df)
                    st.success(f'Trade {trade_to_close} closed successfully!')
        else:
            st.info("No open trades")


    with st.expander("Edit trade"):
        # Let the user select a trade to edit which is already closed:
        closed_trades = df[df['tradeinfo_exit_price'].notna()]
        trade_to_edit = st.selectbox('Select a trade to edit', closed_trades.index)

        # Create the form to edit the selected trade
        with st.form(key='edit_trade_form'):
            st.header(f'Edit Trade {trade_to_edit}')
            edit_trade_data = {}

            image_path = None

            if trade_to_edit is not None:

                if df.loc[trade_to_edit, "human_picture_path"]:
                    image_path = pathlib.Path(str(df.loc[trade_to_edit, "human_picture_path"]))

                    # Check if the path is valid
                if image_path is not None:
                    try:
                        image = Image.open(image_path)
                        st.image(image, caption='Uploaded Image', width=800)
                    except IOError as e:
                        st.write(f"IMAGE: Could not read file, does it exist?..  {image_path}: {e}")
                else:
                    st.write("No Image")

                uploaded_file = st.file_uploader("Change the Image")


                # Create 4 columns
                cols = st.columns(4)

                for col in df.columns:
                    # Categorize the column
                    category = categorize_column(col)
                    default_value = df.loc[trade_to_edit, col]

                    # If the column belongs to one of the categories, create a text input for it in the corresponding column
                    if category >= 0:
                        label = " ".join(col.split("_")[1:])
                        if "sector" in label:
                            edit_trade_data[col] = cols[category].selectbox(f"{label}", [default_value] + data_specs.sectors)
                        elif "market cap" in label:
                            edit_trade_data[col] = cols[category].selectbox(f"{label}",
                                                                            [default_value] + data_specs.market_cap_ranges)
                        elif "risk reward ratio" in label:
                            edit_trade_data[col] = cols[category].selectbox(f"{label}",
                                                                            [default_value] + data_specs.risk_reward_ratios)
                        elif "market sentiment" in label:
                            edit_trade_data[col] = cols[category].selectbox(f"{label}", [default_value] + data_specs.market_sentiment)
                        elif "analyst rating" in label:
                            edit_trade_data[col] = cols[category].selectbox(f"{label}", [default_value] + data_specs.analyst_ratings)
                        elif "mood" in label:
                            edit_trade_data[col] = cols[category].selectbox(f"{label}", [default_value] + data_specs.sorted_moods)
                        elif "mistake" in label:
                            edit_trade_data[col] = cols[category].selectbox(f"{label}", [default_value] + data_specs.trading_mistakes)
                        elif "date" in label:
                            edit_trade_data[col] = cols[category].date_input(f"{label}", default_value)
                        elif "picture path" in label:
                            if uploaded_file:
                                default_value = ROOT_DIR.joinpath('local_storage').joinpath('images').joinpath(uploaded_file.name)
                                with open(default_value, 'wb') as out_file:
                                    out_file.write(uploaded_file.read())

                                # delete old picture
                                try:
                                    os.remove(image_path)
                                    st.info(f"File {image_path} has been deleted.")
                                except FileNotFoundError:
                                    st.info(f"File {image_path} not found.")
                                except PermissionError:
                                    st.info(f"Permission denied.")
                                except Exception as e:
                                    st.info(f"An error occurred: {e}")
                            edit_trade_data[col] = default_value

                        else:
                            if not 'gain' in label:
                                edit_trade_data[col] = cols[category].text_input(f"{label}", value=default_value)
                            else:
                                edit_trade_data[col] = default_value

            else:
                st.info("No closed trades in your trades list.")



            # Create submit and delete buttons in a row
            cols = st.columns(2)
            submit_button = cols[0].form_submit_button(label='Submit Changes')
            delete_button = cols[1].form_submit_button('Delete Trade')

            if submit_button:
                # Update the trade in the DataFrame
                for col in df.columns:
                    df.loc[trade_to_edit, col] = edit_trade_data[col]
                save_data(df)
                st.success(f'Trade {trade_to_edit} updated successfully!')

            if trade_to_edit is not None:
                if delete_button:
                    # Delete the trade from the DataFrame
                    df = df.drop(trade_to_edit)
                    save_data(df)
                    st.success(f'Trade {trade_to_edit} deleted successfully!')


    default_columns = load_selected_columns()
    #default_columns = [get_label(label) for label in default_columns]
    #st.text(default_columns)
    selected_columns = st.multiselect("Select the columns you want to display", df.columns, default=default_columns)

    col1, col2, col3, col4 = st.columns(4)

    if selected_columns:
        # Create a list of all columns in selected_columns containing 'gain'
        gain_columns = [s for s in selected_columns if "gain" in s]

        if gain_columns:
            #st.markdown(styled_df.to_html(escape=False), unsafe_allow_html=True)
            keys = df.columns
            my_dict = {key: key.split('_', 1)[1] for key in keys}
            my_dict["tradeinfo_entry_date"] = st.column_config.DateColumn(
                "entry_date",
                format="DD.MM.YYYY",
                step=1
            )
            my_dict["tradeinfo_exit_date"] = st.column_config.DateColumn(
                "exit_date",
                format="DD.MM.YYYY",
                step=1
            )
            st.dataframe(df.style.applymap(color_negative_red_positive_green, subset=['tradeinfo_gain_percentage']), column_order=selected_columns, column_config=my_dict, use_container_width=True)
        else:
            st.dataframe(df, column_order=selected_columns, column_config=my_dict, use_container_width=True)

        save_selected_columns(selected_columns)
    else:
        st.write("Select columns from selectbox!")


def show_analysis(df):
    backtest.show_backtest()


if __name__ == "__main__":
    main()
