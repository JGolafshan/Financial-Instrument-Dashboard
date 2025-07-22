#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Date: 04/04/2024
    Author: Joshua David Golafshan
    Description: OmniQuant homepage with chunked trending display & backend refresh decoupled.
"""
import time
import yfinance as yf
import streamlit as st
from datetime import datetime
from zoneinfo import ZoneInfo
from curl_cffi import requests
from src.utils.utils import set_page_state
from src.utils.static_values import exchange_timezones

CHUNK_SIZE = 5
BACKEND_REFRESH_RATE = "600s"
INDICES_REFRESH = "20s"


@st.cache_data(ttl=BACKEND_REFRESH_RATE, show_spinner="Refreshing Yahoo Finance data")
def get_data():
    """Fetch fresh gainers, losers, and index data from Yahoo Finance every BACKEND_REFRESH_RATE."""
    session = requests.Session(impersonate="chrome")

    indices = yf.Tickers([
        '^GSPC', '^DJI', '^IXIC', '^RUT', '^FTSE', '^N225', '^GDAXI', '^FCHI', '^HSI', '^AXJO'
    ], session=session)

    indices_info = []
    for ticker in indices.tickers.values():
        try:
            info = ticker.info
            indices_info.append(info)
            time.sleep(0.2)
        except Exception as e:
            print(f"Error fetching data for {ticker.ticker}: {e}")

    return indices_info


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


@st.experimental_fragment(run_every=INDICES_REFRESH)
def indices_display(indices):
    indices_index = get_next_index("indices_index", len(indices))
    display_trending_items(indices, st.columns(CHUNK_SIZE), indices_index)


def display_timezones_items(timezone_data: dict, columns, start_index: int):
    timezone_list = list(timezone_data.items())
    for i, (region, info) in enumerate(timezone_list[start_index:start_index + CHUNK_SIZE]):
        city = info["City"]
        tz_name = info["Timezone"]

        try:
            now_dt = datetime.now(ZoneInfo(tz_name))
            now_time = now_dt.strftime("%H:%M")
            weekday = now_dt.strftime("%A")
        except Exception as e:
            now_time = f"Error"
            weekday = "N/A"

        label = f"{region} ({city}) - {weekday}" if city else f"{region} - {weekday}"

        with columns[i]:
            st.metric(
                label=label,
                value=now_time
            )


@st.experimental_fragment(run_every="8s")
def timezone_display(timezone_data):
    timezone_index = get_next_index("timezone_index", len(timezone_data))
    display_timezones_items(timezone_data, st.columns(CHUNK_SIZE), timezone_index)


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
    timezone_display(exchange_timezones)

    st.markdown("---")
    st.subheader("Global Indices")
    indices = get_data()
    indices_display(indices)


if __name__ == "__main__":
    main()
