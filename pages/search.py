#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Date: 04/04/2024
    Author: Joshua David Golafshan
"""

import streamlit as st
from src import sidebar, cookies
from utils import utils
from utils.utils import set_page_state

st.set_page_config(
    page_title="Instrument Query",
    page_icon="📊",
    layout="centered",
    initial_sidebar_state="collapsed"
)
# Load Default Data
st.markdown(utils.load_css("assets/css/styles.css"), unsafe_allow_html=True)

# Session Data
session_id = cookies.get_session_id()
set_page_state(f"pages/{__name__}")

# Load Components
sidebar.sidebar()
utils.user_component()

with st.container(key="search_container"):
    st.markdown('<div class="center-column">', unsafe_allow_html=True)
    st.header("Query an Instrument")
    search_query = st.text_input("Search over 54,000 available instruments", "", placeholder="AAPL")
    st.markdown('</div>', unsafe_allow_html=True)
    utils.search_logic(search_query)
