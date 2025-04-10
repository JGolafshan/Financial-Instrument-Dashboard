#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Date: 04/04/2024
    Author: Joshua David Golafshan
    Description: A page with a search bar that redirects to instrument.py

"""

import streamlit as st
from src.utils.utils import set_page_state
from src.components.custom_searchbar import custom_search_bar


# Load Components
set_page_state("pages/search.py")

with st.container(key="search_page_container"):
    column_padding_empty1, content, column_padding_empty2 = st.columns([0.1, 0.8, 0.1])

    with content:
        content.header("Search for Instruments")
        content.markdown("#### Search over 54,000 Instruments available")
        custom_search_bar("form_container", "big_search", [0.9, 0.1, 0.1])
