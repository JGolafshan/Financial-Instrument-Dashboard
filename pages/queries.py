#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Date: 04/04/2024
    Author: Joshua David Golafshan
"""

import pandas as pd
import streamlit as st
from typing import Dict
from pymongo import DESCENDING
from src.utils.utils import set_page_state
from src.components.simple_components import title_divider


FILTER_KEYS = ["q", "filter_user_id", "filter_date", "page_number", "size"]
PAGE_SIZES = [25, 50, 100]


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

        if key == "page_number" or key == "size":
            st.query_params[key] = int(value)
            continue

        # Everything else → stripped string
        st.query_params[key] = str(value).strip()

def clear_filters():
    st.session_state["q"] = ""
    st.session_state["filter_date"] = None
    st.session_state["page_number"] = 1
    st.session_state["size"] = PAGE_SIZES[0]

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
def get_data(size: int, page: int, query: dict = None) -> pd.DataFrame:
    """
    Fetches filtered data from MongoDB, returns a batch of records based on page size.
    """
    db = st.session_state.db_client["user_history"]
    collection = db["history"]

    skip = size * (page - 1)
    query = query or {}

    cursor = collection.find(query).sort("datetime", DESCENDING).skip(skip).limit(size)
    items = list(cursor)

    df = pd.DataFrame(items).drop(columns=['_id'], errors='ignore')

    df = df.astype({
        "user_id": "string",
        "datetime": "string",
        "page_url": "string"
    })

    return df


def filter_data(page_url_filter="", date_filter=None, size=1000, page=1) -> pd.DataFrame:
    """
    Fetches data from MongoDB applying only structured filters, no text search.
    """
    query = {}

    if page_url_filter and page_url_filter != "Select a Page URL":
        query["page_url"] = page_url_filter

    if date_filter:
        start = pd.to_datetime(date_filter)
        end = start + pd.Timedelta(days=1)
        query["datetime"] = {"$gte": start, "$lt": end}

    return get_data(size=size, page=page, query=query)

def get_active_filters() -> Dict[str, str]:
    active_filters = {
        "Search": st.session_state.get("q"),
        "Filter Date": st.session_state.get("filter_date"),
    }
    return {k: v for k, v in active_filters.items() if v}


def main():
    set_page_state()

    # Header
    st.title("User Activity")
    st.caption("Explore user activities and interactions on this website, including your own and others' actions.")
    title_divider()

    qp = st.query_params
    search_q = qp.get("q", "")
    filter_date_q = qp.get("filter_date", None)
    page_number_q = int(qp.get("page_number", 1))
    page_size_q = int(qp.get("size", 25))

    # Layout Columns
    filter_column, dataframe_column = st.columns((2, 9), gap="large")

    # Filter sidebar
    with filter_column:
        st.subheader("Filters")

        st.text_input(
            label = "Search Recent Activity",
            value = search_q,
            key = "q",
            placeholder = "Search Recent User Activities",
            on_change = sync_query_params
        )

        st.date_input(
            label="Filter by Date",
            format="YYYY-MM-DD",
            value=filter_date_q,
            key="filter_date",
            on_change=sync_query_params
        )

        batch_size = int(st.selectbox(
            label="Page Size",
            options=PAGE_SIZES,
            index=PAGE_SIZES.index(page_size_q),
            key="size",
            on_change=sync_query_params
        ))

        st.divider()
        active_filters = get_active_filters()

        st.button(
            label=f"Clear Filters ({len(active_filters)})" if active_filters else "Clear Filters",
            width='stretch',
            on_click=clear_filters,
            disabled=not active_filters
        )

    # DataFrame + Pagination
    with dataframe_column:
        # Get data WITHOUT text search filtering on Mongo side
        filtered_df = filter_data(
            date_filter=filter_date_q,
            size=1000,  # TODO Client Side filtering?
            page=page_number_q
        )
        sub_entries =  len(filtered_df)

        # Apply client-side search filter across all string columns
        search_query = search_q.strip()
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
            current_page = st.number_input(
                label="Page Number",
                min_value=1,
                value=page_number_q,
                max_value=total_pages,
                step=1,
                key="page_number",
                on_change=sync_query_params
            )

    # Display DataFrame
    if paged_df.empty:
        pagination.warning("No rows found matching filtering criteria.")

    else:
        pagination.markdown(f"Displaying **{start_idx + 1}** to **{end_idx}** of **{sub_entries}** entries")
        pagination.dataframe(
            paged_df,
            width="stretch",
            height=400,
            hide_index=True,
            column_config={
                "user_id": st.column_config.TextColumn("User ID", width="small"),
                "datetime": st.column_config.TextColumn("Datetime Accessed", width="small"),
                "page_url": st.column_config.TextColumn("Page Url", width="small"),
            }
        )

if __name__ == "__main__":
    main()
