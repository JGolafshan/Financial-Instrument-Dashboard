import uuid
import streamlit as st
import extra_streamlit_components as stx
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
        user_id = str(uuid.uuid4())  # Generate a new UUID
        cookie_manager.set("user_id", user_id)  # Persist in cookies
    st.session_state["user_id"] = user_id

st.markdown(utils.load_css("assets/css/styles.css"), unsafe_allow_html=True)
utils.user_component()

pages = [
    st.Page("pages/home.py", title="Landing Page", icon=":material/show_chart:"),
    st.Page("pages/instrument.py", title="Instrument", icon=":material/show_chart:", url_path="/instrument"),
    st.Page("pages/queries.py", title="Historical Queries", icon=":material/show_chart:", url_path="/history"),
    st.Page("pages/search.py", title="Instrument Query", icon=":material/show_chart:", url_path="/search"),
]

error_page = st.Page("pages/error_page.py", title="Error", icon=":material/show_chart:", url_path="error")

pg = st.navigation(pages, expanded=True)
sidebar.sidebar()


try:
    pg.run()
except Exception as e:
    st.header("Error")
    st.error(f"An unexpected error occurred. Redirecting to error page... \n\n {e.__str__()}")
