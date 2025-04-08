#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Date: 04/04/2024
    Author: Joshua David Golafshan
"""

import pandas as pd
import streamlit as st
from datetime import datetime

from src.utils.test import generate_random_document
from src.utils.utils import set_page_state, insert_document, get_total_documents

set_page_state("pages/queries.py")
st.title("User Activity")


# --- Function to get data from MongoDB ---
@st.cache_data(show_spinner="Loading user history...")
def get_data(size: int, page: int):
    """
    Fetches data from MongoDB, returns a batch of records based on page size.
    """
    db = st.session_state.db_client["user_history"]
    collection = db["history"]

    skip = size * (page - 1)
    cursor = collection.find().skip(skip).limit(size)
    items = list(cursor)

    # Convert ObjectId to str for caching and display
    for item in items:
        item["_id"] = str(item["_id"])

    raw_df = pd.DataFrame(items)
    raw_df.rename(columns={'user_id': 'User ID',
                           'datetime': 'DateTime',
                           "page_url": "Page URL",
                           "use_type": "Type",
                           "page_parameters": "Parameters"
                           }, inplace=True)

    return raw_df


if st.button("Add to db"):
    test = generate_random_document()
    insert_document(**test)
    st.cache_data.clear()  # Invalidate cached data

    # Optionally, re-fetch the data to display updated information
    get_data(size=25, page=1)  # Adjust size/page as needed


# --- Filter Function ---
def filter_data(search_query="", user_id_filter="", date_filter=None, size=10, page=1):
    """
    Filters the data based on user input and returns a DataFrame.
    Calls get_data to fetch the data from MongoDB.
    """
    df = get_data(size=size, page=page)

    # --- Free text search ---
    if search_query and search_query.strip():
        query = search_query.strip().lower()

        # Make columns str's
        df["User ID"] = df["User ID"].astype(str)
        df["DateTime"] = df["DateTime"].astype(str)

        user_id = df["User ID"].str.lower().str.contains(query, na=False)
        datetime_col = df["DateTime"].str.lower().str.contains(query, na=False)
        df = df[user_id | datetime_col]

    # --- User ID filter ---
    if user_id_filter and user_id_filter.strip():
        user_id_query = user_id_filter.strip().lower()
        df = df[df["User ID"].astype(str).str.lower().str.contains(user_id_query, na=False)]

    # --- Date filter ---
    if date_filter:
        df["DateTime"] = pd.to_datetime(df["DateTime"], errors="coerce")
        df = df[df["DateTime"].dt.date == date_filter]

    return df


# --- Sidebar / Filters ---
side_menu = st.columns((9, 2))

with side_menu[1]:
    st.subheader("Filter Options")

    if st.button("Clear All Filters"):
        st.session_state["filter_user_id"] = ""
        st.session_state["filter_date"] = None

    st.text_input("Filter by User ID", key="filter_user_id")
    st.date_input("Filter by Date", value=None, format="YYYY-MM-DD", key="filter_date")

# --- DataFrame + Pagination ---
with side_menu[0]:
    top_menu = st.columns((2, 4, 1))

    # --- Search Box ---
    with top_menu[0]:
        search_box_input = st.text_input("Search", placeholder="Type to search...")

    # --- Page Size ---
    with top_menu[2]:
        batch_size = st.selectbox("Page Size", options=[25, 50, 100], index=0)

    # --- Filter the Data ---
    filtered_df = filter_data(
        search_query=search_box_input,
        user_id_filter=st.session_state.get("filter_user_id", ""),
        date_filter=st.session_state.get("filter_date", None),
        size=batch_size,
        page=1  # Adjust this to allow pagination dynamically
    )

    # --- Pagination Setup ---
    total_entries = get_total_documents()
    total_pages = max((total_entries - 1) // batch_size + 1, 1)

    pagination = st.container()
    bottom_menu = st.columns((7, 4, 1))

    with bottom_menu[2]:
        current_page = st.number_input("Page", min_value=1, max_value=total_pages, step=1, value=1)

    with bottom_menu[0]:
        start_idx = (current_page - 1) * batch_size
        end_idx = min(start_idx + batch_size, total_entries)
        st.markdown(f"Showing **{start_idx + 1}** to **{end_idx}** of **{total_entries}** entries")

    # --- Display Data ---
    if filtered_df.empty:
        pagination.warning("No rows found matching filtering criteria.")
    else:
        # Directly display the data for the selected page and batch size
        start_idx = (current_page - 1) * batch_size
        end_idx = min(start_idx + batch_size, total_entries)
        pagination.dataframe(filtered_df.iloc[start_idx:end_idx], use_container_width=True)
