#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Date: 04/04/2024
Author: Joshua David Golafshan
Description: Streamlit app to list and filter all available financial instruments.
"""

import pandas as pd
import streamlit as st
from src.utils.utils import set_page_state
import orjson

# Set the Streamlit page state and title
set_page_state("pages/instruments.py")

if "filter_search" not in st.session_state:
    st.session_state["filter_search"] = ""


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

    if exchange_name_filter:
        df = df[df["Exchange Name"] == exchange_name_filter]

    if exchange_symbol_filter:
        df = df[df["Exchange Symbol"] == exchange_symbol_filter]

    return df


st.title("Instrument Directory")
st.markdown("""Explore and filter available financial instruments on this website.
               Use the options on the right to filter different categorical variables.""")

dataframe_column, filter_column = st.columns((9, 2))

# Main table display
with dataframe_column:
    col1, col2 = st.columns([0.25, 0.75])
    col1.text_input("Search (Ticker, Company, Exchange)", value=st.session_state.get("filter_search", ""), key="filter_search")

    raw_df = load_clean_ticker_data()
    filtered_df = filter_data(
        raw_df,
        st.session_state.get("filter_search", ""),
        st.session_state.get("filter_exchange_name", ""),
        st.session_state.get("filter_exchange_symbol", "")
    )
    st.dataframe(filtered_df, use_container_width=True, hide_index=True)

# Filter sidebar
with filter_column:
    st.subheader("Filter Options")
    exchange_names = raw_df["Exchange Name"].unique()
    exchange_symbols = raw_df["Exchange Symbol"].unique()
    asset_types = ["Not Implemented"]  # Placeholder for future support

    # Clear filters
    if st.button("Clear All Filters"):
        st.session_state.pop("filter_exchange_name")
        st.session_state.pop("filter_exchange_symbol")
        st.session_state.pop("filter_asset_type")
        st.session_state.pop("filter_search")
        st.rerun()

    # Display Available Filters
    st.selectbox(label="Exchange Name", placeholder="Select an Exchange Name",
                 index=0, options=([""]+list(exchange_names)), key="filter_exchange_name")

    st.selectbox(label="Exchange Symbol", placeholder="Select an Exchange Name",
                 index=0, options=([""]+list(exchange_symbols)), key="filter_exchange_symbol")

    st.selectbox("Asset Type", placeholder="Select an Asset Type", options=asset_types, key="filter_asset_type")

st.markdown(f"Showing **{len(filtered_df)}** out of **{len(raw_df)}** entries")

