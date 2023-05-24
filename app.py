import streamlit as st
import pandas as pd
import os
import pathlib
import data_specs


ROOT_DIR = pathlib.Path(__file__).resolve().parents[0]
filepath_datastore = ROOT_DIR.joinpath('local_storage').joinpath('trades.csv')
st.set_page_config(layout="wide")

if 'page' not in st.session_state:
    st.session_state.page = 'Dashboard'

# https://www.investopedia.com/top-7-technical-analysis-tools-4773275
# https://www.investopedia.com/articles/fundamental-analysis/09/five-must-have-metrics-value-investors.asp

def load_data():
    if os.path.exists(filepath_datastore):
        return pd.read_csv(filepath_datastore)
    else:
        return pd.DataFrame(columns=data_specs.journal_data_df_colums)


def save_data(df):
    df = df.sort_values(by="tradeinfo_entry_date", ascending=False)
    df.to_csv(filepath_datastore, index=False)

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
    st.title('Trading Journal')

    column1, column2, column3 = st.columns(3)
    with column1:
        if st.button('Dashboard'):
            st.session_state.page = "Dashboard"
    with column2:
        if st.button('Trade List'):
            st.session_state.page = "Trade List"
    with column3:
        if st.button('Analysis'):
            st.session_state.page = "Analysis"

    #page = st.sidebar.selectbox("Choose a page", ["Dashboard", "Trade List", "Analysis"])

    df = load_data()

    if st.session_state.page == "Dashboard":
        df = show_dashboard(df)
    elif st.session_state.page == "Trade List":
        df = show_trade_list(df)
    elif st.session_state.page == "Analysis":
        df = show_analysis(df)

    save_data(df)


def show_dashboard(df):
    return df


def show_trade_list(df):
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
        st.write("Select columns from the sidebar to view the data.")

    return df


def show_analysis(df):
    return df


if __name__ == "__main__":
    main()
