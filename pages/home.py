#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Date: 04/04/2024
    Author: Joshua David Golafshan
    Description: This is the default page - the initial page that the user sees.
"""

import streamlit as st
from src.utils.utils import set_page_state

# Load Components
set_page_state("pages/home.py")

st.title("Welcome to the Stock Dashboard")

st.markdown("""
A comprehensive platform for tracking, analyzing, and exploring financial market data. Utilize interactive tools and advanced analytics to support your investment decisions.
""")

st.markdown("---")

cols = st.columns([0.1, 0.4, 0.4, 0.1])

with cols[1]:
    st.subheader("Search Stocks")
    st.write("""
    **Discover and evaluate stocks with robust features:**
    - Interactive price and performance charts  
    - Detailed company profiles and financial metrics  
    - Option pricing using the Black-Scholes model
    """)
    if st.button("Go to Search Stocks"):
        st.switch_page("pages/search.py")  # Use the relative path of your search page script

with cols[2]:
    st.subheader("User Queries")
    st.write("""
    **Access and manage user-generated insights:**
    - Browse and filter historical search queries  
    - Search by user ID or review your previous activity
    - Open the relevant page with the exact parameters the user originally used, duplicating their query and context
    """)
    if st.button("Go to User Queries"):
        st.switch_page("pages/queries.py")  # Adjust this path based on your folder structure

st.markdown("---")

