#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Date: 03/04/2024
    Author: Joshua David Golafshan
"""

import uuid
import datetime
import yfinance as yf
import streamlit as st
import streamlit_javascript
from typing import Optional, Any
from pymongo.errors import DuplicateKeyError
from src.utils.query_handler import QueryHandler


def search_logic(value: str):
    # Remove
    if value:
        st.session_state.code = value
        insert_document(st.session_state.get("user_id"), datetime.datetime.now(datetime.UTC), get_url())
        st.session_state["current_page"] = "pages/instrument.py"
        st.switch_page("pages/instrument.py")

def get_url():
    """
    Returns the real Streamlit page URL using JS.
    Safe against first-render JS timing issues.
    """
    parameters_st = st.query_params

    if st.query_params == 0 or st.query_params is None:
        return st.context.url

    parameters = ""
    for query in parameters_st:
        parameters += f"{query}={parameters_st[query]}&"

    return st.context.url + "?" + parameters[:-1]

def yahoo_data(ticker: str) -> Optional[Any]:
    try:
        return yf.Ticker(ticker)
    except:
        return None


def set_page_state():
    """
    Log a page view once per logical page change.
    """

    current_page = get_url()
    last_page = st.session_state.get("last_logged_page")

    if current_page != last_page:
        st.session_state["last_logged_page"] = current_page

        insert_document(
            user_id=st.session_state.get("user_id"),
            datetime_custom=datetime.datetime.now(datetime.UTC),
            page_url=current_page
        )

@st.cache_resource
def user_identifier():
    """
        Generate a unique user ID for this session if it doesn't exist.
        Persist in session_state.
    """
    if "user_id" not in st.session_state:
        st.session_state.user_id = str(uuid.uuid4())
        print("Generated new user_id:", st.session_state.user_id)
    else:
        print("Existing user_id:", st.session_state.user_id)
    return st.session_state.user_id


def set_root_css():
    check_for_config_theme = st.get_option("theme.base")

    if check_for_config_theme == "light":
        return f"""
            <style>
                :root {{
                    --bg-color: rgba(151, 166, 195, 0.25);
                    --bg-id-color: rgb(240, 242, 247);
                    --text-color: #31333F;
                }}
            </style>
        """
    else:
        return f"""
            <style>
                :root {{
                    --bg-color: rgba(172, 177, 195, 0.25);
                    --bg-id-color: rgb(38, 39, 48);
                    --text-color: #fafafa;
                }}
            </style>
        """


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


# Function to insert a document into MongoDB
def insert_document(user_id, datetime_custom, page_url):
    """
    Inserts a document into the MongoDB collection.
    - Generates an ObjectId for the document.
    - Adds timestamp information to the document.
    """
    db = st.session_state.db_client["user_history"]
    collection = db["history"]

    document = {
        "user_id": user_id,
        "datetime": datetime_custom,
        "page_url": page_url,
    }

    try:
        # Insert the document into the collection
        result = collection.insert_one(document)
        return result.inserted_id

    except DuplicateKeyError:
        st.error(f"Document with user_id {user_id} already exists.")
        return None
    except Exception as e:
        st.error(f"Error inserting document: {e}")
        return None


def get_user_timezone():
    return streamlit_javascript.st_javascript("Intl.DateTimeFormat().resolvedOptions().timeZone")

def init_page():
    user_identifier()

    set_page_state()
