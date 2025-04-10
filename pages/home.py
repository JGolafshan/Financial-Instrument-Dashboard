#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Date: 04/04/2024
    Author: Joshua David Golafshan
    Description: This is the default page - the initial page that the user sees.
"""

import streamlit as st
import yfinance as yf
from src.utils.utils import set_page_state

CHUNK_SIZE = 5


@st.cache_data(ttl="5s", show_spinner="Loading Stock Screener")
def get_data():
    """Fetches fresh gainers and losers data from Yahoo Finance."""
    best_gainers = yf.screen("day_gainers", sortField='percentchange', sortAsc=True)
    worst_losers = yf.screen("day_losers", sortField='percentchange', sortAsc=True)
    return best_gainers, worst_losers


def get_next_index(key, max_length):
    """Cycles index in steps of CHUNK_SIZE and resets when needed."""
    index = st.session_state.get(key, 0)
    index = index + CHUNK_SIZE if index + CHUNK_SIZE < max_length else 0
    st.session_state[key] = index
    return index


def display_trending_items(screen_data, columns, start_index):
    quotes = screen_data["quotes"]
    for i, quote in enumerate(quotes[start_index:start_index + CHUNK_SIZE]):
        with columns[i]:
            try:
                company_name = quote.get("longName") or quote.get("displayName", "Unknown")
                symbol = quote["symbol"]
                price = quote["regularMarketPrice"]
                change = quote["regularMarketChangePercent"]
                st.metric(
                    label=f"{company_name} ({symbol})",
                    value=f"${price:.2f}",
                    delta=f"{change:.2f}%"
                )
            except Exception as e:
                st.warning(f"Error loading stock: {e}")


@st.fragment(run_every="10s")
def trending_display():
    gainers, losers = get_data()
    st.subheader("Global Indices")

    st.subheader("Top performing stocks today")
    gainer_index = get_next_index("gainer_index", len(gainers["quotes"]))
    display_trending_items(gainers, st.columns(CHUNK_SIZE), gainer_index)

    st.subheader("Top underperforming stocks today")
    loser_index = get_next_index("loser_index", len(losers["quotes"]))
    display_trending_items(losers, st.columns(CHUNK_SIZE), loser_index)


# Home page description
def main():
    set_page_state("pages/home.py")

    st.title("Welcome to the Stock Dashboard")
    st.markdown("""
        **A comprehensive platform for tracking, analyzing, and exploring financial market data. 
        Utilize interactive tools and advanced analytics to support your investment decisions.**""")

    st.markdown("""
        Search for stocks with interactive charts, financial metrics, and option pricing tools. 
        Or review user-generated queries with filters for user ID, date, and original parameters.
        """)

    btn1, btn2, empty2 = st.columns([0.15, 0.15, 0.7])

    if btn1.button("Search Instruments"):
        st.switch_page("pages/search.py")

    if btn2.button("View User Activity"):
        st.switch_page("pages/queries.py")

    st.markdown("---")

    # Trending Stock w/ Links

    trending_display()
    st.markdown("---")


if __name__ == "__main__":
    main()
