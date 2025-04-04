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

# Page Configuration
st.set_page_config(
    page_title="Error Page",
    page_icon="📊",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Load Default Data
st.markdown(utils.load_css("assets/css/styles.css"), unsafe_allow_html=True)

# Session Data
session_id = cookies.get_session_id()
set_page_state("pages/error_page.py")

# Load Components
search_query = sidebar.sidebar()
utils.user_component()

st.error(f"⚠️ \n \n Error \n \n **{"An Error Happended..."}** ")

col1, col2 = st.columns([1, 1], gap="small", vertical_alignment="center")

with col1:
    if st.button("Go Back"):
        st.switch_page("app.py")
with col2:
    if st.button("Go To Search"):
        st.switch_page("pages/search.py")
