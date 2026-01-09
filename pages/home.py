#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Date: 04/04/2024
Author: Joshua David Golafshan
Description: OmniQuant homepage with chunked trending display & backend refresh decoupled.
"""

import time
from datetime import datetime
from typing import Optional
from zoneinfo import ZoneInfo

import yfinance as yf
import streamlit as st
from curl_cffi import requests

from src.utils.utils import set_page_state
from src.utils.static_values import exchange_timezones

CHUNK_SIZE = 5
DATA_REFRESH_RATE = 600
INDICES_VISIBILITY_REFRESH = 20
TIMEZONE_VISIBILITY_REFRESH = 8

# Symbol and Name hard coded to reduce call bandwidth
INDEX_TICKERS = [
    {"symbol":'^GSPC', "name": "S&P 500"},
    {"symbol":'^IXIC', "name": "NASDAQ Composite"},
    {"symbol":'^FTSE', "name": "FTSE 100"},
    {"symbol":'^N225', "name": "Nikki 225"},
    {"symbol":'^GDAXI', "name": "DAX P"},
    {"symbol":'^HSI', "name": "HANG SENG INDEX"},
    {"symbol":'^AXJO', "name": "S&P/ASX 200 (^AXJO)"}
]


def calc_pct_change(open_price: float, last_price: float) -> Optional[float]:
    if not open_price or not last_price or open_price <= 0:
        return None
    return (last_price - open_price) / open_price * 100

@st.cache_data(ttl=DATA_REFRESH_RATE, show_spinner="Refreshing Yahoo Finance data")
def fetch_yahoo_data():
    """Fetch Global Indices"""
    session = requests.Session(impersonate="chrome")

    symbols = [idx["symbol"] for idx in INDEX_TICKERS]
    name_map = {idx["symbol"]: idx["name"] for idx in INDEX_TICKERS}

    indices = yf.Tickers(" ".join(symbols), session=session)

    indices_info = []

    for symbol, ticker in indices.tickers.items():
        try:
            fi = ticker.fast_info

            last_price = fi.get("lastPrice")
            open_price = fi.get("open")

            indices_info.append({
                "symbol": symbol,
                "name": name_map.get(symbol, symbol),
                "last_price": last_price,
                "open_price": open_price,
                "pct_change": calc_pct_change(open_price, last_price),
            })

            time.sleep(0.15)  # be kind to Yahoo

        except Exception as e:
            st.warning(f"Failed to fetch {symbol}: {e}")

    return indices_info

def get_rotating_index(key: str, length: int) -> int:
    idx = st.session_state.get(key, 0)
    next_idx = idx + CHUNK_SIZE if idx + CHUNK_SIZE < length else 0
    st.session_state[key] = next_idx
    return idx


def render_chunked(data, render_fn, key: str):
    start = get_rotating_index(key, len(data))
    cols = st.columns(CHUNK_SIZE)

    for col, item in zip(cols, data[start:start + CHUNK_SIZE]):
        with col:
            render_fn(item)

def render_index_card(item: dict):
    price = item["last_price"]
    pct = item["pct_change"]

    st.metric(
        label=f"{item['name']} ({item['symbol']})",
        value = f"${price:.2f}" if price is not None else "N/A",
        delta=f"{pct:.2f}%" if pct is not None else "N/A",
        border=True,
    )

def render_timezone_card(item: dict):
    region, info = item
    city, tz_name = info["City"], info["Timezone"]

    try:
        now = datetime.now(ZoneInfo(tz_name))
        label = f"{region} ({city}) - {now:%A}" if city else f"{region} - {now:%A}"
        value = now.strftime("%H:%M")
    except Exception as e:
        label, value = region, "N/A"

    st.metric(label=label, value=value)

@st.fragment(run_every=INDICES_VISIBILITY_REFRESH)
def indices_fragment(indices_data: dict):
    render_chunked(indices_data, render_index_card, "indices:cursor")


@st.fragment(run_every=TIMEZONE_VISIBILITY_REFRESH)
def timezones_fragment(tz_data: dict):
    render_chunked(list(tz_data.items()), render_timezone_card, "timezones:cursor")



def main():
    set_page_state()

    st.title("Welcome to OmniQuant")

    st.markdown(
        """
        **A comprehensive platform for tracking, analyzing, and exploring financial market data. 
        Utilize interactive tools and advanced analytics to support your investment decisions.**
        """
    )

    st.markdown(
        """
        Search for stocks with interactive charts, financial metrics, and option pricing tools. 
        Or review user-generated queries with filters for user ID, date, and other related parameters.
        """
    )

    btn1, btn2, btn3, _ = st.columns([0.14, 0.14, 0.14, 0.58])
    if btn1.button("Search Instruments"):
        st.switch_page("pages/search.py")
    elif btn2.button("Create a portfolio"):
        st.switch_page("pages/tracker.py")
    elif btn3.button("View User Activity"):
        st.switch_page("pages/queries.py")


    st.divider()
    st.subheader("Global Timezones")
    st.caption("International Timezones • Rotates automatically")
    timezones_fragment(exchange_timezones)

    st.divider()
    st.subheader("Global Indices")
    st.caption("Data delayed • Yahoo Finance • Rotates automatically")
    indices_fragment(fetch_yahoo_data())


if __name__ == "__main__":
    main()
