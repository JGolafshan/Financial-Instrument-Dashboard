#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Date: 04/04/2024
Author: Joshua David Golafshan
Description: OmniQuant homepage with chunked trending display & backend refresh decoupled.
"""

import time
from datetime import datetime
from zoneinfo import ZoneInfo

import yfinance as yf
import streamlit as st
from curl_cffi import requests

from src.utils.utils import set_page_state
from src.utils.static_values import exchange_timezones

CHUNK_SIZE = 5
BACKEND_REFRESH_RATE = "600s"
INDICES_REFRESH = "20s"


@st.cache_data(ttl=BACKEND_REFRESH_RATE, show_spinner="Refreshing Yahoo Finance data")
def fetch_yahoo_data():
    """Fetch fresh gainers, losers, and index data from Yahoo Finance every BACKEND_REFRESH_RATE."""
    session = requests.Session(impersonate="chrome")

    indices = yf.Tickers(['^GSPC', '^DJI', '^IXIC', '^RUT', '^FTSE', '^N225', '^GDAXI', '^FCHI', '^HSI', '^AXJO'])

    indices_info = []
    for ticker in indices.tickers.values():
        try:
            info = ticker.info
            indices_info.append(info)
            time.sleep(0.2)
        except Exception as e:
            print(f"Error fetching data for {ticker.ticker}: {e}")

    print(indices_info)

    return indices_info


def get_next_chunk_index(session_key: str, max_len: int, chunk_size: int = CHUNK_SIZE) -> int:
    """Cycle the index forward by chunk size, wrap around if at end."""
    index = st.session_state.get(session_key, 0)
    index = index + chunk_size if index + chunk_size < max_len else 0
    st.session_state[session_key] = index
    return index


def display_chunked_items(data, columns, start_index, render_fn):
    """Generic display function for chunked metric rendering."""
    chunk = data[start_index:start_index + CHUNK_SIZE]
    for i, item in enumerate(chunk):
        with columns[i]:
            try:
                render_fn(item)
            except Exception as e:
                st.warning(f"Render error: {e}")


def render_stock_metric(quote):
    """Render a single stock metric card."""
    name = quote.get("longName") or quote.get("displayName", "Unknown")
    symbol = quote["symbol"]
    price = quote["regularMarketPrice"]
    change = quote["regularMarketChangePercent"]
    st.metric(border=True, label=f"{name} ({symbol})", value=f"${price:.2f}", delta=f"{change:.2f}%")


def render_timezone_metric(item):
    """Render a single timezone metric card."""
    region, info = item
    city, tz_name = info["City"], info["Timezone"]

    try:
        now = datetime.now(ZoneInfo(tz_name))
        time_str = now.strftime("%H:%M")
        weekday = now.strftime("%A")
    except Exception:
        time_str = "Error"
        weekday = "N/A"

    label = f"{region} ({city}) - {weekday}" if city else f"{region} - {weekday}"
    st.metric(label=label, value=time_str)


@st.fragment(run_every=INDICES_REFRESH)
def display_indices(indices_data):
    start_idx = get_next_chunk_index("indices_index", len(indices_data))
    cols = st.columns(CHUNK_SIZE)
    display_chunked_items(indices_data, cols, start_idx, render_stock_metric)


@st.experimental_fragment(run_every="8s")
def display_timezones_fragment(data):
    start_idx = get_next_chunk_index("timezone_index", len(data))
    cols = st.columns(CHUNK_SIZE)
    timezone_items = list(data.items())
    display_chunked_items(timezone_items, cols, start_idx, render_timezone_metric)


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
    st.subheader("Global Timezones")
    display_timezones_fragment(exchange_timezones)

    st.markdown("---")
    st.subheader("Global Indices")
    indices = fetch_yahoo_data()
    display_indices(indices)


if __name__ == "__main__":
    main()
