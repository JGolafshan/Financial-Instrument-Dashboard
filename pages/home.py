#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Date: 04/04/2024
    Author: Joshua David Golafshan
    Description: This is the default page - the initial page that the user sees.
"""
import time

import streamlit as st
import yfinance as yf
from src.utils.utils import set_page_state

# Load Components
set_page_state("pages/home.py")


@st.cache_data(show_spinner="Loading Stock Screener")
def get_data():
    """
    Fetches filtered data from MongoDB, returns a batch of records based on page size.
    """
    time.sleep(4)
    best_gainers = yf.screen("day_gainers", sortField='percentchange', sortAsc=True)
    worst_losers = yf.screen("day_losers", sortField='percentchange', sortAsc=True)

    return best_gainers, worst_losers


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
    st.switch_page("pages/queries.py")

if btn2.button("View User Activity"):
    st.switch_page("pages/queries.py")

gainers, losers = get_data()

st.markdown("---")

st.subheader("Top performing stocks today")
# st.write("""Updated live from Yahoo Finance, highlighting trending upward stocks.""")

gainer_cols = st.columns(5)
for i, quote in enumerate(gainers["quotes"][:5]):
    with gainer_cols[i]:
        st.metric(
            label=f"{quote['longName']} ({quote['symbol']})",
            value=f"${quote['regularMarketPrice']:.2f}",
            delta=f"{quote['regularMarketChangePercent']:.2f}%"
        )

st.subheader("Top underperforming stocks today")
# st.markdown("""Sorted by largest % loss, track market downturns and identify potential rebounds.""")
loser_cols = st.columns(5)
for i, quote in enumerate(losers["quotes"][:5]):
    with loser_cols[i]:
        st.metric(
            label=f"{quote['shortName']} ({quote['symbol']})",
            value=f"${quote['regularMarketPrice']:.2f}",
            delta=f"{quote['regularMarketChangePercent']:.2f}%",
        )

st.markdown("---")
