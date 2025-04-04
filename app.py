#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Date: 03/04/2024
    Author: Joshua David Golafshan
"""

import streamlit as st
from src import sidebar, cookies
from utils import utils
from utils.utils import set_page_state

# Page Configuration
st.set_page_config(
    page_title="Home Page",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)
# Load Default Data
st.markdown(utils.load_css("assets/css/styles.css"), unsafe_allow_html=True)

# Session Data
session_id = cookies.get_session_id()
set_page_state("pages/home.py")

# Load Components
search_query = sidebar.sidebar()
utils.user_compoenet()

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

