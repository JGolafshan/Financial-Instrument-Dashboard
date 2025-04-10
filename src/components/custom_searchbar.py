#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Date: 04/010/2024
    Author: Joshua David Golafshan
"""

import streamlit as st
from src.utils.utils import search_logic


def custom_search_bar(form_key, input_key, col_widths=None):
    with st.form(form_key, border=False, clear_on_submit=True):
        cols = st.columns(col_widths, gap="small")

        with cols[0]:
            search_query = st.text_input(
                label="Search For a Ticker/Symbol:",
                placeholder="e.g. AAPL TSLA",
                label_visibility='collapsed',
                key=input_key
            )
        with cols[1]:
            submitted = st.form_submit_button('🔍')

        if search_query and submitted:
            search_logic(search_query)
