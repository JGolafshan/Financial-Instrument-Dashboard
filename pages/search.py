#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Date: 04/04/2024
    Author: Joshua David Golafshan
    Description: A page with a search bar that redirects to instrument.py

"""

import streamlit as st
from src.utils.utils import set_page_state, search_logic

# Load Components
set_page_state("pages/search.py")


# A page that just contains a search bar with text
with st.container(key="search_page_container"):
    st.markdown('<div class="center-column" style="max-width: 700px; align-items:basline">', unsafe_allow_html=True)
    st.header("Query an Instrument")

    with st.container(key="side_bar_search_bar"):
        search_columns = st.columns([0.9, 0.2])
        with search_columns[0]:
            search_query = st.text_input("Search For a Ticker/Symbol:", "", placeholder="AAPL", key="big_search")

        with search_columns[1]:
            if st.button("🔍", use_container_width=True):
                if search_query:
                    search_logic(search_query)
    st.markdown('</div>', unsafe_allow_html=True)
