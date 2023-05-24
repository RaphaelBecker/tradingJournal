import streamlit as st
import pandas as pd
import os
import pathlib
import data_specs


ROOT_DIR = pathlib.Path(__file__).resolve().parents[0]
st.set_page_config(layout="wide")

# https://www.investopedia.com/top-7-technical-analysis-tools-4773275
# https://www.investopedia.com/articles/fundamental-analysis/09/five-must-have-metrics-value-investors.asp

def load_data():
    filepath = ROOT_DIR.joinpath('local_storage').joinpath('trades.csv')
    if os.path.exists(filepath):
        return pd.read_csv(filepath)
    else:
        return pd.DataFrame(columns=data_specs.journal_data_df_colums)


def save_data(df):
    df = df.sort_values(by="tradeinfo_entry_date", ascending=False)
    df.to_csv('data.csv', index=False)

def save_selected_columns(columns):
    with open('selected_columns.txt', 'w') as f:
        for column in columns:
            f.write(column + '\n')

def load_selected_columns():
    try:
        with open('selected_columns.txt', 'r') as f:
            return [line.strip() for line in f.readlines()]
    except FileNotFoundError:
        return []

def color_negative_red_positive_green(val):
    """
    Takes a scalar and returns a string with
    the css property `'color: red'` for negative
    strings, `'color: green'` for positive, black otherwise.
    """
    color = 'red' if val < 0 else 'green' if val > 0 else 'black'
    return 'color: %s' % color

def main():
    st.title('Trading Journal')
    page = "Dashboard"
    column1, column2, column3 = st.columns(3)
    with column1:
        if st.button('Dashboard'):
            page = "Dashboard"
    with column2:
        if st.button('Trade List'):
            page = "Trade List"
    with column3:
        if st.button('Analysis'):
            page = "Analysis"

    #page = st.sidebar.selectbox("Choose a page", ["Dashboard", "Trade List", "Analysis"])

    df = load_data()

    if page == "Dashboard":
        df = show_dashboard(df)
    elif page == "Trade List":
        df = show_trade_list(df)
    elif page == "Analysis":
        df = show_analysis(df)

    save_data(df)


def show_dashboard(df):
    return df


def show_trade_list(df):
    default_columns = load_selected_columns()
    selected_columns = st.multiselect("Select the columns you want to display", df.columns, default=default_columns)

    col1, col2, col3, col4 = st.columns(4)

    if selected_columns:
        sort_options = ["None"] + df.columns.tolist()
        with col1:
            sort_column = st.selectbox("Select column to sort by", sort_options)
        with col2:
            ascending = st.checkbox("sort descending")

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
        st.write("Select columns from the sidebar to view the data.")
    return df


def show_analysis(df):
    with st.form(key='new_trade_form'):
        st.header('Add a New Trade')
        new_trade_data = {}

        cols = st.columns(4)
        for i, col in enumerate(df.columns):
            new_trade_data[col] = cols[i % 4].text_input(f"New Trade {col}")

        submit_button = st.form_submit_button(label='Submit New Trade')

        if submit_button:
            # Append the new trade to the DataFrame
            df = df.append(new_trade_data, ignore_index=True)
            st.success('New trade added successfully!')

    # Create a new column that combines the details we want to display
    df['Trade Details'] = 'Index: ' + df.index.astype(str) + '  Ticker: ' + df['tradeinfo_Ticker'] + '  Entry Date: ' + df['tradeinfo_entry_date'].astype(str) + '   Entry Price:' + df['tradeinfo_entry_price'].astype(str)


    # Let the user select a trade to edit
    trade_to_edit = st.selectbox('Select a trade to edit', df['Trade Details'])

    # Get the index of the selected trade
    trade_to_edit_index = df[df['Trade Details'] == trade_to_edit].index[0]

    with st.form(key='edit_trade_form'):
        st.header(f'Edit Trade {trade_to_edit_index}')
        edit_trade_data = {}

        cols = st.columns(4)
        for i, col in enumerate(df.columns):
            default_value = df.loc[trade_to_edit_index, col]
            edit_trade_data[col] = cols[i % 4].text_input(f"Trade {trade_to_edit_index} {col}", value=default_value)

        submit_button = st.form_submit_button(label='Submit Changes')

        if submit_button:
            # Update the trade in the DataFrame
            for col in df.columns:
                df.loc[trade_to_edit_index, col] = edit_trade_data[col]

            st.success(f'Trade {trade_to_edit_index} updated successfully!')

    return df


if __name__ == "__main__":
    main()
