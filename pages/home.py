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

# Load Components
set_page_state("pages/home.py")


@st.cache_data(show_spinner="Loading Stock Screener")
def get_data():
    """
    Fetches filtered data from MongoDB, returns a batch of records based on page size.
    """
    best_gainers = yf.screen("day_gainers", sortField='percentchange', sortAsc=True)
    worst_losers = yf.screen("day_losers", sortField='percentchange', sortAsc=True)

    return best_gainers, worst_losers


def display_trending_items(screen_data, columns):
    for i, quote in enumerate(screen_data["quotes"][:5]):
        with columns[i]:
            try:
                company_name = quote['longName']
            except KeyError:
                company_name = quote['displayName']

            st.metric(
                label=f"{company_name} ({quote['symbol']})",
                value=f"${quote['regularMarketPrice']:.2f}",
                delta=f"{quote['regularMarketChangePercent']:.2f}%",
            )


# Home page description

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

st.markdown("---")

# Trending Stock w/ Links

gainers, losers = get_data()

st.subheader("Top performing stocks today")
display_trending_items(gainers, st.columns(5))

st.subheader("Top underperforming stocks today")
display_trending_items(losers, st.columns(5))

st.markdown("---")
