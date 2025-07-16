#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Date: 04/04/2024
    Author: Joshua David Golafshan
    Description: OmniQuant homepage with chunked trending display & backend refresh decoupled.
"""

import time
import streamlit as st
import yfinance as yf
from src.utils.utils import set_page_state

CHUNK_SIZE = 5
BACKEND_REFRESH_RATE = "600s"
TRENDING_REFRESH = "120s"
INDICES_REFRESH = "180s"


@st.cache_data(ttl=BACKEND_REFRESH_RATE, show_spinner="Refreshing Yahoo Finance data")
def get_data():
    """Fetch fresh gainers, losers, and index data from Yahoo Finance every BACKEND_REFRESH_RATE."""
    best_gainers = yf.screen("day_gainers", sortField='percentchange', sortAsc=True)
    worst_losers = yf.screen("day_losers", sortField='percentchange', sortAsc=True)

    indices = yf.Tickers([
        '^GSPC', '^DJI', '^IXIC', '^RUT', '^FTSE', '^N225', '^GDAXI', '^FCHI', '^HSI', '^AXJO'
    ])

    indices_info = []
    for ticker in indices.tickers.values():
        try:
            info = ticker.info
            indices_info.append(info)
            time.sleep(0.2)
        except Exception as e:
            print(f"Error fetching data for {ticker.ticker}: {e}")

    return indices_info, best_gainers, worst_losers


def get_next_index(key, max_length):
    """Cycles index in steps of CHUNK_SIZE and resets when needed."""
    index = st.session_state.get(key, 0)
    index = index + CHUNK_SIZE if index + CHUNK_SIZE < max_length else 0
    st.session_state[key] = index
    return index


def display_trending_items(screen_data, columns, start_index):
    for i, quote in enumerate(screen_data[start_index:start_index + CHUNK_SIZE]):
        with columns[i]:
            try:
                company_name = quote.get("longName") or quote.get("displayName", "Unknown")
                symbol = quote["symbol"]
                price = quote["regularMarketPrice"]
                change = quote["regularMarketChangePercent"]
                st.metric(
                    border=True,
                    label=f"{company_name} ({symbol})",
                    value=f"${price:.2f}",
                    delta=f"{change:.2f}%"
                )
            except Exception as e:
                st.warning(f"Error loading stock: {e}")


@st.fragment(run_every=TRENDING_REFRESH)
def trending_display(gainers, losers):
    st.subheader("Top Stocks Today")
    gainer_index = get_next_index("gainer_index", len(gainers["quotes"]))
    display_trending_items(gainers["quotes"], st.columns(CHUNK_SIZE), gainer_index)

    st.subheader("Worst Stocks Today")
    loser_index = get_next_index("loser_index", len(losers["quotes"]))
    display_trending_items(losers["quotes"], st.columns(CHUNK_SIZE), loser_index)


@st.fragment(run_every=INDICES_REFRESH)
def indices_display(indices):
    st.subheader("Global Indices")
    indices_index = get_next_index("indices_index", len(indices))
    display_trending_items(indices, st.columns(CHUNK_SIZE), indices_index)


def main():
    set_page_state("pages/home.py")
    st.title("Welcome to OmniQuant")

    st.markdown("""
        **A comprehensive platform for tracking, analyzing, and exploring financial market data. 
        Utilize interactive tools and advanced analytics to support your investment decisions.**
    """)
    st.markdown("""
        Search for stocks with interactive charts, financial metrics, and option pricing tools. 
        Or review user-generated queries with filters for user ID, date, and original parameters.
    """)

    btn1, btn2, _ = st.columns([0.15, 0.15, 0.7])
    if btn1.button("Search Instruments"):
        st.switch_page("pages/search.py")
    if btn2.button("View User Activity"):
        st.switch_page("pages/queries.py")

    st.markdown("---")

    indices, gainers, losers = get_data()

    indices_display(indices)
    trending_display(gainers, losers)

    st.markdown("---")


if __name__ == "__main__":
    main()
