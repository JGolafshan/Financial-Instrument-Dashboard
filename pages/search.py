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

with st.container(key="search_page_container"):
    column_padding_empty1, content, column_padding_empty2 = st.columns([0.1, 0.8, 0.1])

    with content:
        content.header("Search for Instruments")
        content.markdown("#### Search over 54,000 Instruments available")

        with st.form('form_container', border=False, clear_on_submit=True):
            col1, col2 = st.columns([0.95, 0.05])

            with col1:
                search_query = st.text_input(
                    label="Search For a Ticker/Symbol:",
                    placeholder="e.g. AAPL, TSLA",
                    label_visibility='collapsed',
                    key="big_search"
                )
            with col2:
                submitted = st.form_submit_button('🔍')

            if search_query and submitted:
                search_logic(search_query)
