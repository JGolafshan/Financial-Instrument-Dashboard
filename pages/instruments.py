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
from typing import Dict
from src.utils.utils import set_page_state
from src.components.simple_components import title_divider

FILTER_KEYS = ["q", "exchange_name", "exchange_symbol", "asset_type"]

def sync_query_params():
    for key in FILTER_KEYS:
        value = st.session_state.get(key, "").strip()
        if value:
            st.query_params[key] = value
        elif key in st.query_params:
            del st.query_params[key]

def clear_filters():
    for key in FILTER_KEYS:
        st.session_state[key] = ""
    st.query_params.clear()

@st.cache_data(show_spinner="Loading ticker data")
def load_clean_ticker_data() -> pd.DataFrame:
    with open("static/tickers.json", "rb") as f:
        data = orjson.loads(f.read())

    df = pd.DataFrame(data)

    # Ensure consistent data types
    df = df.astype({
        "ticker": "string",
        "company_name": "string",
        "exchange_name": "string",
        "exchange_code": "string",
    })

    return df

@st.cache_data
def get_filter_options(df: pd.DataFrame):
    exchange_names = sorted(df["exchange_name"].dropna().unique())
    exchange_symbols = sorted(df["exchange_code"].dropna().unique())
    return exchange_names, exchange_symbols

def filter_data(df: pd.DataFrame, search_query="", exchange_name_filter="", exchange_symbol_filter="") -> pd.DataFrame:
    filtered_df = df.copy()
    if search_query := search_query.strip().lower():
        mask = (
            df["ticker"].str.contains(search_query, case=False, na=False) |
            df["company_name"].str.contains(search_query, case=False, na=False) |
            df["exchange_name"].str.contains(search_query, case=False, na=False) |
            df["exchange_code"].str.contains(search_query, case=False, na=False)
        )
        filtered_df = filtered_df[mask]

    if exchange_name_filter:
        filtered_df = filtered_df[filtered_df["exchange_name"] == exchange_name_filter]

    if exchange_symbol_filter:
        filtered_df = filtered_df[filtered_df["exchange_code"] == exchange_symbol_filter]

    return filtered_df

def get_active_filters() -> Dict[str, str]:
    active_filters = {
        "Search": st.session_state.get("q"),
        "Exchange Name": st.session_state.get("exchange_name"),
        "Exchange Symbol": st.session_state.get("exchange_symbol"),
    }
    return {k: v for k, v in active_filters.items() if v}

def main():
    set_page_state()

    # Query params
    qp = st.query_params
    search_q = qp.get("q", "")
    exchange_name_q = qp.get("exchange_name", "")
    exchange_symbol_q = qp.get("exchange_symbol", "")

    # Header
    st.title("Instrument Directory")
    st.caption("Explore and filter available financial instruments. Search by ticker, company name, or exchange.")
    title_divider()

    # Load data
    raw_df = load_clean_ticker_data()
    exchange_names, exchange_symbols = get_filter_options(raw_df)

    # Layout
    filter_column, dataframe_column = st.columns((2, 9), gap="large")

    # Filters
    with filter_column:
        st.subheader("Filters")

        search_input = st.text_input(
            "Search",
            value=search_q,
            key="q",
            placeholder="Search ticker, company, or exchange",
            on_change=sync_query_params
        )

        st.selectbox(
            "Exchange Name",
            options=[""] + exchange_names,
            format_func=lambda x: x or "All",
            index=(exchange_names.index(exchange_name_q) + 1) if exchange_name_q in exchange_names else 0,
            key="exchange_name",
            on_change=sync_query_params
        )

        st.selectbox(
            "Exchange Symbol",
            options=[""] + exchange_symbols,
            format_func=lambda x: x or "All",
            index=(exchange_symbols.index(exchange_symbol_q) + 1) if exchange_symbol_q in exchange_symbols else 0,
            key="exchange_symbol",
            on_change=sync_query_params
        )

        st.divider()

        active_filters = get_active_filters()
        st.button(
            f"Clear Filters ({len(active_filters)})" if active_filters else "Clear Filters",
            width='stretch',
            on_click=clear_filters,
            disabled=not active_filters
        )

    # Table
    with dataframe_column:
        filtered_df = filter_data(
            raw_df,
            search_query=search_input,
            exchange_name_filter=exchange_name_q,
            exchange_symbol_filter=exchange_symbol_q,
        )

        if filtered_df.empty:
            st.warning("No instruments match your filters.")
            st.button("Clear filters", on_click=clear_filters)
        else:
            st.markdown(
                f"Displaying **{len(filtered_df):,}** of **{len(raw_df):,}** instruments"
            )

            st.dataframe(
                filtered_df,
                hide_index=True,
                width='stretch',
                height=450,
                column_config={
                    "ticker": st.column_config.TextColumn("Ticker", width="small"),
                    "company_name": st.column_config.TextColumn("Company Name", width="medium"),
                    "exchange_name": st.column_config.TextColumn("Exchange Name", width="small"),
                    "exchange_code": st.column_config.TextColumn("Exchange Symbol", width="small"),
                }
            )

if __name__ == "__main__":
    main()
