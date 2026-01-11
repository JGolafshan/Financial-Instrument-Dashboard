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
from src.utils.utils import init_page
from src.utils.query_handler import QueryDataType, QueryHandler
from src.components.simple_components import title_divider


PAGE_SIZES = [25, 50, 100]
query_handler = QueryHandler([
    QueryDataType("q", str, ""),
    QueryDataType("filter_date", pd.Timestamp, None),
    QueryDataType("page_number", int, 1),
    QueryDataType("size", int, 25),
])


@st.cache_data(show_spinner="Loading user history...", ttl="10s")
def get_data(size: int, page: int, query: dict = None):
    db = st.session_state.db_client["user_history"]
    collection = db["history"]

    skip = size * (page - 1)
    query = query or {}

    total_count = collection.count_documents(query)
    cursor = (
        collection.find(query)
        .sort("datetime", DESCENDING)
        .skip(skip)
        .limit(size)
    )

    df = pd.DataFrame(list(cursor)).drop(columns=["_id"], errors="ignore")
    if not df.empty:
        df["datetime"] = pd.to_datetime(df["datetime"], utc=True)

    return df, total_count


def filter_data(page_url_filter="", date_filter=None, size=1000, page=1):
    """
    Fetches data from MongoDB applying structured filters.
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
    init_page()
    query_handler.init_query_parameters()

    # Header
    st.title("User Activity")
    st.caption("Explore user activities and interactions on this website, including your own and others' actions.")
    title_divider()

    # Layout Columns
    filter_column, dataframe_column = st.columns((2, 9), gap="large")

    # Filter sidebar
    with filter_column:
        st.subheader("Filters")
        st.text_input(
            label="Search Recent Activity",
            value=st.query_params.get("q", ""),
            key="q",
            placeholder="Search Recent User Activities",
            on_change=query_handler.sync_query_params,
        )

        st.date_input(
            label="Filter by Date",
            value=st.query_params.get("filter_date", None),
            key="filter_date",
            on_change=query_handler.sync_query_params,
        )

        # Page size selectbox
        page_size_val = st.session_state.get("size", PAGE_SIZES[0])
        st.selectbox(
            label="Page Size",
            options=PAGE_SIZES,
            index=PAGE_SIZES.index(page_size_val),
            key="size",
            on_change=query_handler.sync_query_params,
        )

        # Clear filters
        active_filters = get_active_filters()
        st.divider()
        st.button(
            label=f"Clear Filters ({len(active_filters)})" if active_filters else "Clear Filters",
            width="stretch",
            on_click=query_handler.clear,
            disabled=not active_filters,
        )

    # Data table & pagination
    with dataframe_column:
        filtered_df, total_entries = filter_data(
            date_filter=st.session_state.get("filter_date"),
            size=st.session_state.get("size", PAGE_SIZES[0]),
            page=st.session_state.get("page_number", 1),
        )

        # Client-side search
        search_query = st.session_state.get("q", "").strip()
        if search_query:
            mask = pd.Series(False, index=filtered_df.index)
            for col in filtered_df.select_dtypes(include="object").columns:
                mask |= filtered_df[col].str.contains(search_query, case=False, na=False)
            filtered_df = filtered_df[mask]

        # Pagination
        batch_size = st.session_state.get("size", PAGE_SIZES[0])
        total_pages = max((len(filtered_df) - 1) // batch_size + 1, 1)
        current_page = st.session_state.get("page_number", 1)
        current_page = min(max(current_page, 1), total_pages)

        start_idx = (current_page - 1) * batch_size
        end_idx = min(start_idx + batch_size, len(filtered_df))
        paged_df = filtered_df.iloc[start_idx:end_idx]

        pagination = st.container()

        bottom_menu = st.columns((7, 4, 2))
        with bottom_menu[2]:
            st.number_input(
                label="Page Number",
                min_value=1,
                max_value=total_pages,
                value=current_page,
                step=1,
                key="page_number",
                on_change=query_handler.sync_query_params,
            )

    # Display DataFrame
    if paged_df.empty:
        pagination.warning("No rows found matching filtering criteria.")

    else:
        pagination.markdown(f"Displaying **{start_idx + 1}** to **{end_idx}** of **{len(filtered_df)}** entries")
        pagination.dataframe(
            paged_df,
            width="stretch",
            height=400,
            hide_index=True,
            column_config={
                "user_id": st.column_config.TextColumn("User ID", width="small"),
                "datetime": st.column_config.DatetimeColumn("Datetime Accessed", width="small"),
                "page_url": st.column_config.LinkColumn("Page Url", width="small"),
            }
        )

if __name__ == "__main__":
    main()
