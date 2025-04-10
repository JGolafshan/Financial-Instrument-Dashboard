#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Date: 04/04/2024
    Author: Joshua David Golafshan
"""

import streamlit as st
from src.components.custom_searchbar import custom_search_bar


def sidebar():
    st.sidebar.title("📊 Stock Dashboard")

    with st.sidebar:
        custom_search_bar("search_bar_container", "small_search", [0.8, 0.1, 0.1])
    add_navigation_links()
    author_details()


def add_navigation_links():
    # Add navigation links to the sidebar
    st.sidebar.page_link("pages/home.py", label="Home", icon=":material/home_filled:")
    st.sidebar.page_link("pages/instrument.py", label="Instrument Dashboard", icon=":material/dashboard:")
    st.sidebar.page_link("pages/instruments.py", label="Instruments", icon=":material/explore:")
    st.sidebar.page_link("pages/queries.py", label="Queries", icon=":material/history:")


def author_details():
    # Creator container w/ linked-in link
    linked_in_link = "https://au.linkedin.com/in/jgd000"
    st.sidebar.markdown(
        f"""
            <div id="creator-container">
                <p><code class="code_block">Created by:</code></p>
                <a href="{linked_in_link}" target="_blank">
                    <img src="https://cdn-icons-png.flaticon.com/512/174/174857.png" width="25" height="25">
                    <code class="code_block" style="display:inline;">Joshua David Golafshan</code>
                </a>
            </div>
        """, unsafe_allow_html=True)
