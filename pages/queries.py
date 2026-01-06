#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Date: 04/04/2024
    Author: Joshua David Golafshan
"""

import pandas as pd
import streamlit as st
from pymongo import DESCENDING

from src.components.simple_components import title_divider
from src.utils.utils import set_page_state
from src.utils.static_values import static_page_names, static_page_types


FILTER_KEYS = ["q", "filter_user_id", "filter_page_url", "filter_type", "filter_date", "page_number"]

def sync_query_params():
    for key in FILTER_KEYS:
        value = st.session_state.get(key)

        # Remove empty values
        if value in ("", None):
            st.query_params.pop(key, None)
            continue

        if key == "filter_date":
            st.query_params[key] = value
            continue

        if key == "page_number":
            st.query_params[key] = int(value)
            continue

        # Everything else → stripped string
        st.query_params[key] = str(value).strip()


def clear_filters():
    for key in FILTER_KEYS:
        st.session_state[key] = ""
    st.query_params.clear()


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


def filter_data(page_url_filter="", type_filter="", date_filter=None, size=1000, page=1):
    """
    Fetches data from MongoDB applying only structured filters, no text search.
    """
    query = {}

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
    sync_query_params()

    # Header
    st.title("User Activity")
    st.caption("""Explore user activities and interactions on this website, including your own and others' actions.""")
    title_divider()

    qp = st.query_params
    search_q = qp.get("q", "")
    filter_page_url_q = qp.get("filter_page_url", "")
    filter_type_q = qp.get("filter_type", "")
    filter_date_q = qp.get("filter_date", "")
    page_number_q = int(qp.get("page_number", 1))

    # Layout Columns
    filter_column, dataframe_column = st.columns((2, 9), gap="large")

    # Filter sidebar
    with filter_column:
        st.subheader("Filters")

        st.text_input(
            label = "Search Recent Activity",
            value = st.session_state.get("q", ""),
            key = "q",
            placeholder = "Search Recent User Activities",
            on_change = sync_query_params
        )
        st.selectbox(
            "Filter by Page URL",
            options = [""] + static_page_names,
            format_func = lambda x: x or "Select a Page URL",
            index = (static_page_names.index(filter_page_url_q) + 1) if filter_page_url_q in static_page_names else 0,
            key = "filter_page_url",
            on_change=sync_query_params
            )
        st.selectbox(
                "Filter by Page Type",
                options=[""] + static_page_types,
                format_func=lambda x: x or "Select a Page Status",
                index=(static_page_types.index(filter_type_q) + 1) if filter_type_q in static_page_types else 0,
                key="filter_type",
                on_change=sync_query_params
            )

        st.date_input("Filter by Date", format="YYYY-MM-DD", value=st.session_state.get("filter_date", None), key="filter_date", on_change=sync_query_params)
        batch_size = int(st.selectbox("Page Size", options=[25, 50, 100], index=0))

        # Active filter summary (used to count the number of filters)
        active_filters = {
            "Search": st.session_state.get("q"),
            "Page URL": st.session_state.get("filter_page_url"),
            "Filter Type": st.session_state.get("filter_type"),
            "Filter Date": st.session_state.get("filter_date"),
        }
        active_filters = {k: v for k, v in active_filters.items() if v}

        st.divider()

        st.button(
            f"Clear Filters ({len(active_filters)})" if active_filters else "Clear Filters",
            width='stretch',
            on_click=clear_filters,
            disabled=not active_filters
        )

    # DataFrame + Pagination
    with dataframe_column:
        # Get data WITHOUT text search filtering on Mongo side
        filtered_df, sub_entries = filter_data(
            page_url_filter=filter_page_url_q,
            type_filter=filter_type_q,
            date_filter=filter_date_q,
            size=1000,  # TODO Client Side filtering?
            page=page_number_q
        )

        # Apply client-side search filter across all string columns
        search_query = st.session_state["q"].strip()
        if search_query:
            mask = pd.Series(False, index=filtered_df.index)
            for col in filtered_df.columns:
                if filtered_df[col].dtype == object:
                    mask |= filtered_df[col].str.contains(search_query, case=False, na=False)
            filtered_df = filtered_df[mask]
            sub_entries = filtered_df.shape[0]

        # Pagination calculations
        total_pages = max((sub_entries - 1) // batch_size + 1, 1)
        current_page = page_number_q
        current_page = min(max(current_page, 1), total_pages)  # clamp page number

        start_idx = (current_page - 1) * batch_size
        end_idx = min(start_idx + batch_size, sub_entries)

        paged_df = filtered_df.iloc[start_idx:end_idx]

        pagination = st.container()

        bottom_menu = st.columns((7, 4, 2))
        with bottom_menu[2]:
            current_page = st.number_input("Page Number", min_value=1, max_value=total_pages, step=1, key="page_number")

    # Display DataFrame
    if paged_df.empty:
        pagination.warning("No rows found matching filtering criteria.")
    else:
        pagination.markdown(f"Displaying **{start_idx + 1}** to **{end_idx}** of **{sub_entries}** entries")
        pagination.dataframe(paged_df, width="stretch", height=400, hide_index=True)


if __name__ == "__main__":
    main()
