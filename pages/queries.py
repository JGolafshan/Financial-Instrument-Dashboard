#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Date: 04/04/2024
    Author: Joshua David Golafshan
"""

import pandas as pd
import streamlit as st
from src.utils.utils import set_page_state, get_total_documents
from src.utils.static_values import  static_page_names,static_page_types

set_page_state("pages/queries.py")

if "filter_search" not in st.session_state:
    st.session_state["filter_search"] = ""

if "filter_user_id" not in st.session_state:
    st.session_state["filter_user_id"] = ""

if "filter_page_url" not in st.session_state:
    st.session_state["filter_page_url"] = "Select a Page URL"

if "filter_type" not in st.session_state:
    st.session_state["filter_type"] = "Select a Page Status"

if "filter_date" not in st.session_state:
    st.session_state["filter_date"] = None


# Function to get data from MongoDB
@st.cache_data(show_spinner="Loading user history...")
def get_data(size: int, page: int):
    """
    Fetches data from MongoDB, returns a batch of records based on page size.
    """
    db = st.session_state.db_client["user_history"]
    st.cache_data.clear()
    collection = db["history"]

    skip = size * (page - 1)
    cursor = collection.find().sort("datetime", -1).skip(skip).limit(size)
    items = list(cursor)
    print(items)

    # Convert ObjectId to str for caching and display
    for item in items:
        item["_id"] = str(item["_id"])

    raw_df = pd.DataFrame(items)
    raw_df = raw_df.drop(columns=['_id'], errors='ignore')

    raw_df.rename(columns={'user_id': 'User ID',
                           'datetime': 'DateTime',
                           "page_url": "Page URL",
                           "use_type": "Type",
                           "page_parameters": "Parameters"
                           }, inplace=True)

    return raw_df


# Filter Function
def filter_data(search_query="", user_id_filter="", page_url_filter="", type_filter="", date_filter=None, size=10,
                page=1):
    """
    Filters the data based on user input and returns a DataFrame.
    Calls get_data to fetch the data from MongoDB.
    """
    df = get_data(size=size, page=page)

    # Search bar
    if search_query := search_query.strip().lower():
        matches = (
                df["User ID"].str.lower().str.contains(search_query, na=False) |
                df["Page URL"].str.lower().str.contains(search_query, na=False) |
                df["Type"].str.lower().str.contains(search_query, na=False)
        )
        df = df[matches]

    # User ID filter
    if user_id_filter and user_id_filter.strip():
        user_id_query = user_id_filter.strip().lower()
        df = df[df["User ID"].astype(str).str.lower().str.contains(user_id_query, na=False)]

    # Date filter
    if date_filter:
        df["DateTime"] = pd.to_datetime(df["DateTime"], errors="coerce")
        df = df[df["DateTime"].dt.date == date_filter]

    # Page URL filter
    if page_url_filter and page_url_filter != "Select a Page URL":
        df = df[df["Page URL"] == page_url_filter]

    # Type filter
    if type_filter and type_filter != "Select a Page Status":
        df = df[df["Type"] == type_filter]

    return df


st.title("User Activity")
st.markdown("""Explore user activities and interactions on this website, including your own and others' actions.""")

dataframe_column, filter_column = st.columns((9, 2))
search_input_container, empty1, page_size_container = dataframe_column.columns((2, 4, 1))

# DataFrame + Pagination
with dataframe_column:
    # Search Box
    with search_input_container:
        search_box_input = st.text_input(label="Search Recent Activity",
                                         value=st.session_state.get("filter_search", ""),
                                         key="filter_search", placeholder="Search Instruments")

    # Page Size
    with page_size_container:
        batch_size = st.selectbox("Page Size", options=[25, 50, 100], index=0)

    # Filter the Data
    filtered_df = filter_data(
        search_query=search_box_input,
        user_id_filter=st.session_state.get("filter_user_id", ""),
        page_url_filter=st.session_state.get("filter_page_url", ""),
        type_filter=st.session_state.get("filter_type", ""),
        date_filter=st.session_state.get("filter_date", None),
        size=batch_size,
        page=st.session_state.get("page_number", 1)
    )

    # Pagination Setup
    total_entries = get_total_documents()
    total_pages = max((total_entries - 1) // batch_size + 1, 1)

    pagination = st.container()

    bottom_menu = st.columns((7, 4, 2))
    with bottom_menu[2]:
        current_page = st.number_input("Page Number", min_value=1, max_value=total_pages, step=1, value=1,
                                       key="page_number")

    with bottom_menu[0]:
        start_idx = (current_page - 1) * batch_size
        end_idx = min(start_idx + batch_size, total_entries)
        st.markdown(f"Showing **{start_idx + 1}** to **{end_idx}** of **{total_entries}** entries")

# Filter
with filter_column:
    st.subheader("Filter Options")

    if st.button("Clear All Filters"):
        st.session_state.pop("filter_search")
        st.session_state.pop("filter_user_id")
        st.session_state.pop("filter_page_url")
        st.session_state.pop("filter_type")
        st.session_state.pop("filter_date")
        st.rerun()

    st.text_input(label="Filter by User ID", placeholder="Filter by User ID", key="filter_user_id")

    st.selectbox(label="Filter by Page URL", placeholder="Select a Page URL", index=0,
                 options=static_page_names, key="filter_page_url")
    print(list(filtered_df["Page URL"].unique()))
    st.selectbox(label="Filter by Page Type", placeholder="Select a Page Status", index=0,
                 options=static_page_types, key="filter_type")

    st.date_input("Filter by Date", value=None, format="YYYY-MM-DD", key="filter_date")

# --- Display Data ---
if filtered_df.empty:
    pagination.warning("No rows found matching filtering criteria.")
else:
    pagination.dataframe(filtered_df, use_container_width=True, hide_index=True)
