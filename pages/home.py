#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Date: 04/04/2024
    Author: Joshua David Golafshan
"""

import streamlit as st

st.markdown("""
    ## 🏠 **Welcome to the Stock Dashboard**
    Your all-in-one platform to track, analyze, and explore stock data. Get started with these key features:

    ### 🔍 **<a href='/search' target='_self'>Search Stocks</a>**  
    Find and analyze stocks with ease:
    - Interactive price charts 📈  
    - Comprehensive company insights 🏢  
    - Black-Scholes model for option pricing 📊  

    ### 📌 **<a href='/queries' target='_self'>User Queries</a>**
    - Browse and filter queries from other users 🗂️  
    - Search by user ID or review your past queries 🔎  

    **Use the sidebar to navigate or jump straight into analysis with the search bar!** 🚀  
""", unsafe_allow_html=True)
