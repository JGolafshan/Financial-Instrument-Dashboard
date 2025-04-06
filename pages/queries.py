#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Date: 04/04/2024
    Author: Joshua David Golafshan
"""

import streamlit as st
import pandas as pd
import pymongo

from src.utils.utils import set_page_state

# Load Components
set_page_state("pages/queries.py")


st.title("User Activity")


# --- Load dataset ---
@st.cache_data
def load_data(file_path):
    df = pd.read_json(file_path)
    df.rename(columns={'user_id': 'User ID', 'date_time': 'DateTime'}, inplace=True)
    return df


@st.cache_data(show_spinner=False)
def split_frame(input_df, rows):
    return [input_df.iloc[i:i + rows, :] for i in range(0, len(input_df), rows)]


# --- File path ---
raw_data = [
    {
        "user_id": "6a1e8b5b-dac9-4277-aca6-c07045b5ee06",
        "date_time": "2025-04-04 10:20:30",
        "url": "/instrument",
        "type": "viewed",
        "link": "/instrument?code=GOOG"
    },
    {
        "user_id": "6a1e8b5b-dac9-4277-aca6-c07045b5ee06",
        "date_time": "2025-04-04 10:20:30",
        "url": "/instrument",
        "type": "viewed",
        "link": "/instrument?code=AAPL"
    }
]
dataset = pd.json_normalize(raw_data)
dataset.rename(columns={'user_id': 'User ID', 'date_time': 'DateTime', "url": "URL", "type": "Type"}, inplace=True)


# --- Filter Function ---
def filter_data(search_query="", user_id_filter="", date_filter=None):
    """
    Filters the dataset using:
    - Free text search on 'ticker' and 'company_name'
    - Exact match for user ID (case-insensitive)
    - Date match for DateTime column (YYYY-MM-DD)
    """
    df = dataset.copy()

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
        # Ensure 'DateTime' column is datetime if not already
        if not pd.api.types.is_datetime64_any_dtype(df["DateTime"]):
            df["DateTime"] = pd.to_datetime(df["DateTime"], errors="coerce")

        df = df[df["DateTime"].dt.date == date_filter]

    return df


side_menu = st.columns((9, 2))

# --- Layout: Advanced Filtering
with side_menu[1]:
    st.subheader("Filter Options")
    if st.button("Clear All Filters"):
        st.session_state["filter_user_id"] = ""
        st.session_state["filter_date"] = None

    st.text_input("Filter by User ID", key="filter_user_id")
    st.date_input("Filter by Date", value=None, format="YYYY-MM-DD", key="filter_date")

# --- Layout: Dataframe + Pagination
with side_menu[0]:
    top_menu = st.columns((2, 4, 1))

    # Search input
    with top_menu[0]:
        search_box_input = st.text_input("Search", placeholder="Type to search...")
        filtered_df = filter_data(search_box_input, st.session_state.get("filter_user_id", None),
                                  st.session_state.get("filter_date", None))

    # Page size selector
    with top_menu[2]:
        batch_size = st.selectbox("Page Size", options=[25, 50, 100], index=0)

    # Pagination controls
    pagination = st.container()
    bottom_menu = st.columns((7, 4, 1))

    total_entries = len(filtered_df)
    total_pages = max((total_entries - 1) // batch_size + 1, 1)

    with bottom_menu[2]:
        current_page = st.number_input("Page", min_value=1, max_value=total_pages, step=1)

    with bottom_menu[0]:
        start_idx = (current_page - 1) * batch_size
        end_idx = min(start_idx + batch_size, total_entries)
        st.markdown(f"Showing **{start_idx}** to **{end_idx - 1}** of **{total_entries - 1}** entries")

    # Display filtered and paginated data
    if filtered_df.empty:
        pagination.warning("No rows found matching filtering criteria.")
    else:
        pages = split_frame(filtered_df, batch_size)
        pagination.dataframe(pages[current_page - 1], use_container_width=True)