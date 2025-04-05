#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Date: 04/04/2024
    Author: Joshua David Golafshan
    Description: List all instruments available

"""

import pandas as pd
import streamlit as st
from src.utils.utils import set_page_state

# Load Components
set_page_state(f"pages/{__name__}")

# Sample stock data in JSON format
stock_data = [
    {"ticker": "AAA", "company_name": "First Priority Clo Bond ETF", "exchange_name": "AMEX",
     "exchange_code": "American Stock Exchange"},
    {"ticker": "BBB", "company_name": "Second Priority Clo Bond ETF", "exchange_name": "NASDAQ",
     "exchange_code": "NASDAQ Stock Exchange"},
    {"ticker": "CCC", "company_name": "Third Priority Clo Bond ETF", "exchange_name": "NYSE",
     "exchange_code": "New York Stock Exchange"},
    {"ticker": "DDD", "company_name": "Fourth Priority Clo Bond ETF", "exchange_name": "AMEX",
     "exchange_code": "American Stock Exchange"},
    {"ticker": "EEE", "company_name": "Fifth Priority Clo Bond ETF", "exchange_name": "NASDAQ",
     "exchange_code": "NASDAQ Stock Exchange"},
]

# Convert to DataFrame for display
stock_df = pd.DataFrame(stock_data)

# Streamlit app UI
st.title("Instrument List")

# Filter by exchange
exchange_options = stock_df['exchange_name'].unique()
selected_exchange = st.selectbox("Select Exchange", exchange_options)

# Filter the DataFrame based on the selected exchange
filtered_stock_df = stock_df[stock_df['exchange_name'] == selected_exchange]

# Display the filtered stock data
st.dataframe(filtered_stock_df)
