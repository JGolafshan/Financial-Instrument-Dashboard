#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Date: 04/04/2024
    Author: Joshua David Golafshan
"""

import pandas as pd
import streamlit as st
from src.utils.utils import set_page_state

# Load Components
set_page_state(f"pages/{__name__}")


st.title("Historical Queries")


@st.cache_data(show_spinner=False)
def load_data(file_path):
    dataset = pd.read_json(file_path)
    dataset.rename(columns={
        'user_id': 'User ID',
        'date_time': 'DateTime'
    }, inplace=True)
    return dataset


@st.cache_data(show_spinner=False)
def split_frame(input_df, rows):
    df = [input_df.iloc[i: i + rows, :] for i in range(0, len(input_df), rows)]

    return df


side_menu = st.columns((9, 2))

with side_menu[0]:
    file_path = r"C:\Users\JGola\Documents\Fivver\Projects\Financial-Instrument-Dashboard\data\queries.json"
    if file_path:
        dataset = load_data(file_path)
        top_menu = st.columns((2, 4, 1))
        with top_menu[0]:
            search_query = st.text_input("", "", placeholder="Search")

        with top_menu[2]:
            batch_size = st.selectbox("Page Size", options=[25, 50, 100])

        pagination = st.container()

        bottom_menu = st.columns((7, 4, 1))

        with bottom_menu[2]:
            total_pages = (
                int(len(dataset) / batch_size) if int(len(dataset) / batch_size) > 0 else 1
            )
            current_page = st.number_input(
                "Page", min_value=1, max_value=total_pages, step=1
            )
        with bottom_menu[0]:
            st.markdown(
                f"Showing **{(current_page * batch_size) - batch_size}** to **{(current_page * batch_size) - 1}** of **{int(len(dataset))}** entries")

        pages = split_frame(dataset, batch_size)
        pagination.dataframe(data=pages[current_page - 1], use_container_width=True)

with side_menu[1]:
    st.title("sss")
    # Clear all filters:
    # Filter by my id
    # Filter By datetime
