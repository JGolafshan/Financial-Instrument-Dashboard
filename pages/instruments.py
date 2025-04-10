#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Date: 04/04/2024
Author: Joshua David Golafshan
Description: Streamlit app to list and filter all available financial instruments.
"""

import orjson
import pandas as pd
import streamlit as st
from src.utils.utils import set_page_state


@st.cache_data(show_spinner="Loading ticker data")
def load_clean_ticker_data():
    """Load and clean ticker data from JSON file."""
    with open("static/tickers.json") as f:
        data = orjson.loads(f.read())
    df = pd.DataFrame(data)
    df.rename(columns={
        'ticker': 'Ticker',
        'company_name': 'Company Name',
        'exchange_name': 'Exchange Name',
        'exchange_code': 'Exchange Symbol',
    }, inplace=True)
    return df


def filter_data(df, search_query="", exchange_name_filter="", exchange_symbol_filter=""):
    """Filter dataframe based on user inputs."""
    if search_query := search_query.strip().lower():
        matches = (
                df["Ticker"].str.lower().str.contains(search_query, na=False) |
                df["Company Name"].str.lower().str.contains(search_query, na=False) |
                df["Exchange Name"].str.lower().str.contains(search_query, na=False) |
                df["Exchange Symbol"].str.lower().str.contains(search_query, na=False)
        )
        df = df[matches]

    if exchange_name_filter and exchange_name_filter != "Select an Exchange Name":
        df = df[df["Exchange Name"] == exchange_name_filter]

    if exchange_symbol_filter and exchange_symbol_filter != "Select an Exchange Symbol":
        df = df[df["Exchange Symbol"] == exchange_symbol_filter]

    return df


def main():
    set_page_state("pages/instruments.py")
    st.title("Instrument Directory")
    st.markdown("""Explore and filter available financial instruments on this website.
                       Use the options on the right to filter different categorical variables.""")

    default_filters = {
        "filter_search": "",
        "filter_exchange_name": "Select an Exchange Name",
        "filter_exchange_symbol": "Select an Exchange Symbol",
        "filter_asset_type": "Select an Asset Type",
    }
    for key, val in default_filters.items():
        st.session_state.setdefault(key, val)

    dataframe_column, filter_column = st.columns((9, 2))

    # Main table display
    with dataframe_column:
        col1, col2 = st.columns([0.25, 0.75])
        col1.text_input(label="Search (Ticker, Company, Exchange)", value=st.session_state.get("filter_search", ""),
                        key="filter_search", placeholder="Search Instruments")

        raw_df = load_clean_ticker_data()
        filtered_df = filter_data(
            raw_df,
            st.session_state.get("filter_search", ""),
            st.session_state.get("filter_exchange_name", ""),
            st.session_state.get("filter_exchange_symbol", "")
        )
        pagination = st.container()

    # Filter sidebar
    with filter_column:
        st.subheader("Filter Options")
        exchange_names = sorted(raw_df["Exchange Name"].dropna().unique().tolist())
        exchange_symbols = sorted(raw_df["Exchange Symbol"].dropna().unique().tolist())
        asset_types = ["Select an Asset Type", "Not Implemented"]

        with st.form(key="filter_form", border=False):
            st.selectbox(label="Filter by Exchange Name", options=(["Select an Exchange Name"] + exchange_names),
                         key="filter_exchange_name")
            st.selectbox(label="Filter by Exchange Symbol", options=["Select an Exchange Symbol"] + exchange_symbols,
                         key="filter_exchange_symbol")
            st.selectbox("Filter by Asset Type", placeholder="Select an Asset Type", options=asset_types,
                         key="filter_asset_type")

            # Clear filters
            clear, apply = st.columns(2)
            with clear:
                if st.form_submit_button("Clear Filters"):
                    for key in default_filters:
                        st.session_state.pop(key)
                    st.rerun()

            with apply:
                st.form_submit_button("Apply Filters")

    st.markdown(f"Showing **{len(filtered_df)}** out of **{len(raw_df)}** entries")

    # --- Display Data ---
    if filtered_df.empty:
        pagination.warning("No rows found matching filtering criteria.")

    else:
        pagination.dataframe(filtered_df, use_container_width=True, hide_index=True)


if __name__ == "__main__":
    main()
