#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Date: 04/04/2024
    Author: Joshua David Golafshan
"""

import uuid
import pymongo
import streamlit as st
from src.utils import utils
from src.components import sidebar
import extra_streamlit_components as stx
from pymongo.server_api import ServerApi

with st.empty():
    @st.cache_resource
    def get_cookie_manager():
        return stx.CookieManager()

    cookie_manager = get_cookie_manager()
    user_id = cookie_manager.get("user_id") or str(uuid.uuid4())
    cookie_manager.set("user_id", user_id)
    st.session_state["user_id"] = user_id


@st.cache_resource
def get_db_connection():
    mong_data = st.secrets['mongo']
    uri = f"mongodb+srv://{mong_data['username']}:{mong_data['password']}@{mong_data['db_name']}/?appName={mong_data['appName']}"
    return pymongo.MongoClient(uri, server_api=ServerApi('1'))


@st.cache_resource
def get_pages():
    return [
        st.Page("pages/home.py", title="Landing Page", icon=":material/show_chart:", url_path="/home", default=True),
        st.Page("pages/instrument.py", title="Instrument", icon=":material/show_chart:", url_path="/instrument"),
        st.Page("pages/instruments.py", title="Instruments", icon=":material/show_chart:", url_path="/instruments"),
        st.Page("pages/queries.py", title="Historical Queries", icon=":material/show_chart:", url_path="/history"),
        st.Page("pages/search.py", title="Instrument Query", icon=":material/show_chart:", url_path="/search"),
    ]


st.session_state["db_client"] = get_db_connection()

# TODO Makes these cached / resource since its loaded everytime...
st.markdown(utils.load_css("assets/css/styles.css"), unsafe_allow_html=True)
utils.user_component()

pg = st.navigation(get_pages(), expanded=True)
sidebar.sidebar()

try:
    pg.run()

except Exception as e:
    st.header("Error")
    st.error(f"An unexpected error occurred. Redirecting to error page... \n\n {e.__str__()}")
