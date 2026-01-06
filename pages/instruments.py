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
def load_clean_ticker_data():
    with open("static/tickers.json", "rb") as f:
        data = orjson.loads(f.read())

    df = pd.DataFrame(data).rename(columns={
        "ticker": "Ticker",
        "company_name": "Company Name",
        "exchange_name": "Exchange Symbol",
        "exchange_code": "Exchange Name",
    })
    return df


@st.cache_data
def get_filter_options(df):
    return (
        sorted(df["Exchange Name"].dropna().unique()),
        sorted(df["Exchange Symbol"].dropna().unique())
    )


def filter_data(df, search_query="", exchange_name_filter="", exchange_symbol_filter=""):
    if search_query := search_query.strip().lower():
        mask = (
            df["Ticker"].str.contains(search_query, case=False, na=False) |
            df["Company Name"].str.contains(search_query, case=False, na=False) |
            df["Exchange Name"].str.contains(search_query, case=False, na=False) |
            df["Exchange Symbol"].str.contains(search_query, case=False, na=False)
        )
        df = df[mask]

    if exchange_name_filter:
        df = df[df["Exchange Name"] == exchange_name_filter]

    if exchange_symbol_filter:
        df = df[df["Exchange Symbol"] == exchange_symbol_filter]

    return df


def main():
    set_page_state("pages/instruments.py")

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

        # Active filter summary (used to count the number of filters)
        active_filters = {
            "Search": st.session_state.get("q"),
            "Exchange Name": st.session_state.get("exchange_name"),
            "Exchange Symbol": st.session_state.get("exchange_symbol"),
        }
        active_filters = {k: v for k, v in active_filters.items() if v}

        st.divider()

        st.button(
            f"Clear Filters ({len(active_filters)})" if active_filters else "Clear Filters",
            width='stretch',
            on_click=clear_filters,
            disabled=not active_filters
        )

    # Table
    with dataframe_column:
        with st.spinner("Filtering instruments…"):
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
                height=450
            )


if __name__ == "__main__":
    main()
