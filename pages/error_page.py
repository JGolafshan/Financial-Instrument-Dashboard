#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Date: 04/04/2024
    Author: Joshua David Golafshan
"""
import streamlit as st
from src.utils.utils import set_page_state

# Load Components
set_page_state("pages/error_page.py")


# Show an error message
st.error(f"⚠️ \n \n Error \n \n **{"An Error Happended..."}** ")
col1, col2 = st.columns([1, 1], gap="small", vertical_alignment="center")
with col1:
    if st.button("Go Back"):
        st.switch_page("app.py")
with col2:
    if st.button("Go To Search"):
        st.switch_page("pages/search.py")
