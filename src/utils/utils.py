#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Date: 03/04/2024
    Author: Joshua David Golafshan
"""
import datetime
import yfinance as yf
import streamlit as st
from typing import Optional, Any
from pymongo.errors import DuplicateKeyError


def search_logic(value: str):
    if value:
        st.session_state.code = value

        insert_document(st.session_state.get("user_id"), datetime.datetime.now(), st.session_state["current_page"],
                        [{"search_value": value}], "searched")
        st.session_state["current_page"] = "pages/instrument.py"
        st.switch_page("pages/instrument.py")
        st.experimental_rerun()  # Rerun to trigger page change


def yahoo_data(ticker: str) -> Optional[Any]:
    try:
        return yf.Ticker(ticker)
    except:
        return None


def user_component():
    # HTML for floating user ID box with a copy button
    session_id = st.session_state.get("user_id", "USER-123456")

    st.markdown(f"""
        <div class="floating-user-id">
            <span>🆔 </span>
            <span>{session_id}</span>
        </div>
    """, unsafe_allow_html=True)


def set_page_state(page: str):
    """Set the current page in session state and navigate if needed."""
    if st.session_state.get("current_page") != page:
        st.session_state.current_page = page
        user_id = st.session_state.get("user_id")
        insert_document(user_id, datetime.datetime.now(), page, [], "viewed")


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
def insert_document(user_id, datetime_custom, page_url, page_parameters, use_type):
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
        "page_parameters": page_parameters,
        "use_type": use_type
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


def get_total_documents():
    # Connect to MongoDB collection
    db = st.session_state.db_client["user_history"]
    collection = db["history"]

    # Get the total count of documents in the collection
    total_documents = collection.count_documents({})
    print(total_documents)

    return total_documents
