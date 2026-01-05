#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Date: 04/04/2024
    Author: Joshua David Golafshan
"""

import pandas as pd
import streamlit as st
from pymongo import DESCENDING

from src.utils.utils import set_page_state
from src.utils.static_values import static_page_names, static_page_types


def extract_search_value(val):
    if isinstance(val, list) and val:
        first = val[0]
        if isinstance(first, dict):
            return first.get('search_value', 'N/A') or 'N/A'
        else:
            return str(first)
    elif isinstance(val, dict):
        return val.get('search_value', 'N/A') or 'N/A'
    elif isinstance(val, str):
        return val
    return 'N/A'


# Function to get data from MongoDB
@st.cache_data(show_spinner="Loading user history...", ttl="10s")
def get_data(size: int, page: int, query: dict = None):
    """
    Fetches filtered data from MongoDB, returns a batch of records based on page size.
    """
    st.cache_data.clear()
    db = st.session_state.db_client["user_history"]
    collection = db["history"]

    skip = size * (page - 1)
    query = query or {}
    queries_size = collection.count_documents(query)

    cursor = collection.find(query).sort("datetime", DESCENDING).skip(skip).limit(size)
    items = list(cursor)

    for item in items:
        item["_id"] = str(item["_id"])

    df = pd.DataFrame(items).drop(columns=['_id'], errors='ignore')

    if "page_parameters" in df.columns:
        df["page_parameters"] = df["page_parameters"].apply(extract_search_value)
    else:
        df["page_parameters"] = "N/A"

    df.rename(columns={
        'user_id': 'User ID',
        'datetime': 'DateTime',
        "page_url": "Page URL",
        "use_type": "Type",
        "page_parameters": "Parameters"
    }, inplace=True)

    return df, queries_size


def filter_data(user_id_filter="", page_url_filter="", type_filter="", date_filter=None, size=1000, page=1):
    """
    Fetches data from MongoDB applying only structured filters, no text search.
    """
    query = {}

    if user_id_filter := user_id_filter.strip():
        query["user_id"] = {"$regex": user_id_filter, "$options": "i"}

    if page_url_filter and page_url_filter != "Select a Page URL":
        query["page_url"] = page_url_filter

    if type_filter and type_filter != "Select a Page Status":
        query["use_type"] = type_filter

    if date_filter:
        start = pd.to_datetime(date_filter)
        end = start + pd.Timedelta(days=1)
        query["datetime"] = {"$gte": start, "$lt": end}

    return get_data(size=size, page=page, query=query)


def main():
    set_page_state("pages/queries.py")

    st.title("User Activity")
    st.markdown("""Explore user activities and interactions on this website, including your own and others' actions.""")

    # --- Initialize Session State Filters ---
    default_filters = {
        "filter_search": "",
        "filter_user_id": "",
        "filter_page_url": "Select a Page URL",
        "filter_type": "Select a Page Status",
        "filter_date": None,
        "page_number": 1
    }
    for key, val in default_filters.items():
        st.session_state.setdefault(key, val)

    # Layout Columns
    dataframe_column, filter_column = st.columns((9, 2))
    search_input_container, empty1, page_size_container = dataframe_column.columns((2, 4, 1))

    # DataFrame + Pagination
    with dataframe_column:
        # Search Box
        search_input_container.text_input(
            label="Search Recent Activity",
            value=st.session_state.get("filter_search", ""),
            key="filter_search",
            placeholder="Search Recent User Activities"
        )

        # Page Size
        batch_size = page_size_container.selectbox("Page Size", options=[25, 50, 100], index=0)

        # Get data WITHOUT text search filtering on Mongo side
        filtered_df, sub_entries = filter_data(
            user_id_filter=st.session_state["filter_user_id"],
            page_url_filter=st.session_state["filter_page_url"],
            type_filter=st.session_state["filter_type"],
            date_filter=st.session_state["filter_date"],
            size=1000,  # TODO Client Side filtering?
            page=1
        )

        # Apply client-side search filter across all string columns
        search_query = st.session_state["filter_search"].strip()
        if search_query:
            mask = pd.Series(False, index=filtered_df.index)
            for col in filtered_df.columns:
                if filtered_df[col].dtype == object:
                    mask |= filtered_df[col].str.contains(search_query, case=False, na=False)
            filtered_df = filtered_df[mask]
            sub_entries = filtered_df.shape[0]

        # Pagination calculations
        total_pages = max((sub_entries - 1) // batch_size + 1, 1)
        current_page = st.session_state["page_number"]
        current_page = min(max(current_page, 1), total_pages)  # clamp page number

        start_idx = (current_page - 1) * batch_size
        end_idx = min(start_idx + batch_size, sub_entries)

        paged_df = filtered_df.iloc[start_idx:end_idx]

        pagination = st.container()

        bottom_menu = st.columns((7, 4, 2))
        with bottom_menu[2]:
            current_page = st.number_input("Page Number", min_value=1, max_value=total_pages, step=1, key="page_number")

        with bottom_menu[0]:
            st.markdown(f"Showing **{start_idx + 1}** to **{end_idx}** of **{sub_entries}** entries")

    # Filter sidebar
    with filter_column:
        st.subheader("Filter Options")
        with st.form(key="filter_form", border=False):
            st.text_input("Filter by User ID", key="filter_user_id", placeholder="e.g., c3b831ed-979d...")
            st.selectbox("Filter by Page URL", options=static_page_names, key="filter_page_url")
            st.selectbox("Filter by Page Type", options=static_page_types, key="filter_type")
            st.date_input("Filter by Date", format="YYYY-MM-DD", key="filter_date")

            clear, apply = st.columns(2)
            with clear:
                if st.form_submit_button("Clear Filters"):
                    for key in default_filters:
                        st.session_state.pop(key)
                    st.session_state["page_number"] = 1
                    st.rerun()

            with apply:
                st.form_submit_button("Apply Filters")

    # Display DataFrame
    if paged_df.empty:
        pagination.warning("No rows found matching filtering criteria.")
    else:
        pagination.dataframe(paged_df, width="stretch", height=400, hide_index=True)


if __name__ == "__main__":
    main()
