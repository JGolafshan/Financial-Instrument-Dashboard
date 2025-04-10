import uuid
import streamlit as st
import extra_streamlit_components as stx
import pymongo
from pymongo.server_api import ServerApi
from src.components import sidebar
from src.utils import utils

with st.empty():
    @st.cache_resource
    def get_manager():
        return stx.CookieManager()


    cookie_manager = get_manager()

    # Retrieve the existing user_id from cookies
    user_id = cookie_manager.get("user_id")

    # If no user_id exists, generate and store one
    if user_id is None:
        user_id = str(uuid.uuid4())
        cookie_manager.set("user_id", user_id)
    st.session_state["user_id"] = user_id


@st.cache_resource
def get_db_connection():
    mong_data = st.secrets['mongo']
    uri = f"mongodb+srv://{mong_data['username']}:{mong_data['password']}@{mong_data['db_name']}/?appName={mong_data['appName']}"
    client = pymongo.MongoClient(uri, server_api=ServerApi('1'))
    return client


if "db_client" not in st.session_state:
    st.session_state["db_client"] = get_db_connection()

st.markdown(utils.load_css("assets/css/styles.css"), unsafe_allow_html=True)
utils.user_component()

pages = [
    st.Page("pages/home.py", title="Landing Page", icon=":material/show_chart:"),
    st.Page("pages/instrument.py", title="Instrument", icon=":material/show_chart:", url_path="/instrument"),
    st.Page("pages/instruments.py", title="Instruments", icon=":material/show_chart:", url_path="/instruments"),
    st.Page("pages/queries.py", title="Historical Queries", icon=":material/show_chart:", url_path="/history"),
    st.Page("pages/search.py", title="Instrument Query", icon=":material/show_chart:", url_path="/search"),
]

pg = st.navigation(pages, expanded=True)
sidebar.sidebar()

try:
    pg.run()
except Exception as e:
    st.header("Error")
    st.error(f"An unexpected error occurred. Redirecting to error page... \n\n {e.__str__()}")
