#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Date: 03/04/2024
    Author: Joshua David Golafshan
"""
from typing import Optional, Any
import yfinance as yf
import streamlit as st
import streamlit_js_eval



def yahoo_data(ticker: str) -> Optional[Any]:
    try:
        return yf.Ticker(ticker)
    except:
        return None


def search_logic(value: str):
    print(st.session_state.get("current_page"))
    if value:
        if "code" in st.session_state and st.session_state.get("current_page") == "pages/instrument.py":
            st.session_state.code = value
        else:
            st.session_state.code = value
            set_page_state("pages/instrument.py")
            st.switch_page("pages/instrument.py")


def user_compoenet():
    # HTML for floating user ID box with a copy button
    session_id = st.session_state.get("session_id", "USER-123456")

    st.markdown(f"""
        <div class="floating-user-id">
            <span>🆔 </span>
            <span>{session_id}</span>
            <button class="copy-btn" id="copyButton">Copy</button>
        </div>
    """, unsafe_allow_html=True)


def set_page_state(page: str):
    """Set the current page in session state and navigate if needed."""
    if st.session_state.get("current_page") != page:
        st.session_state.current_page = page


def load_css(file_path: str) -> str:
    """
    Load and apply a custom CSS file to the Streamlit app.

    This function abstracts the CSS from the Streamlit app by reading
    a CSS file and injecting it into the app using `st.markdown()`.

    :param file_path: Path to the CSS file.
    :raises FileNotFoundError: If the specified file does not exist.
    :raises Exception: If the file cannot be read.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            css = f.read()
        return f"<style>{css}</style>"
    except FileNotFoundError:
        st.error(f"CSS file not found: {file_path}")
    except Exception as e:
        st.error(f"Error loading CSS file: {e}")
