#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Date: 04/04/2024
    Author: Joshua David Golafshan
    Description: A page with a search bar that redirects to instrument.py

"""

import streamlit as st
from src.utils import utils
from src.utils.utils import set_page_state

# Load Components
set_page_state(f"pages/{__name__}")

# A page that just contains a search bar with text
with st.container(key="search_container"):
    st.markdown('<div class="center-column" style="max-width: 700px;">', unsafe_allow_html=True)
    st.header("Query an Instrument")
    search_query = st.text_input("Search over 54,000 available instruments", "", placeholder="AAPL", key="big_search")
    st.markdown('</div>', unsafe_allow_html=True)
    utils.search_logic(search_query)