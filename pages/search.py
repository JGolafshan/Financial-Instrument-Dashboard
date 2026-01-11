#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Date: 04/04/2024
    Author: Joshua David Golafshan
    Description: A page with a search bar that redirects to instrument.py
"""

import streamlit as st
from src.utils.utils import init_page
from src.components.simple_components import title_divider
from src.components.custom_searchbar import custom_search_bar


def main():
    init_page()

    with st.container(key="search_page_container"):
        column_padding_empty1, content, column_padding_empty2 = st.columns([0.1, 0.8, 0.1])

        with content:
            content.header("Search for Instruments")
            content.caption("Search over 54,000 Instruments available")
            title_divider()

            if "search_warning" in st.session_state:
                st.warning(st.session_state["search_warning"])
                del st.session_state["search_warning"]
                del st.session_state["code"]

            custom_search_bar("form_container", "big_search", [0.9, 0.1, 0.1])


if __name__ == "__main__":
    main()
