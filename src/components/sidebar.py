#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Date: 04/04/2024
    Author: Joshua David Golafshan
"""

import streamlit as st
from src.utils import utils


def sidebar():
    st.sidebar.title("📊 Stock Dashboard")

    # Search for a stock
    search_query = st.sidebar.text_input("Search For a Ticker/Symbol:", "", placeholder="AAPL")
    utils.search_logic(search_query)

    # Show the navigation
    st.sidebar.page_link("pages/home.py", label="Home", icon=":material/home_filled:")
    st.sidebar.page_link("pages/instrument.py", label="Instrument Dashboard", icon=":material/dashboard:")
    # st.sidebar.page_link("pages/instruments.py", label="Instruments", icon=":material/explore:")
    st.sidebar.page_link("pages/queries.py", label="Queries", icon=":material/history:")

    # Creator container w/ linked-in link
    st.sidebar.markdown(
        """
        <div id="creator-container">
            <p><code class="code_block">Created by:</code></p>
            <a href="https://au.linkedin.com/in/jgd000" target="_blank">
                <img src="https://cdn-icons-png.flaticon.com/512/174/174857.png" width="25" height="25">
                <code class="code_block" style="display:inline;">Joshua David Golafshan</code>
            </a>
        </div>
        """, unsafe_allow_html=True
    )
