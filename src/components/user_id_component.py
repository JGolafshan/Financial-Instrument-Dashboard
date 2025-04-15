import streamlit as st


def user_component():
    # HTML for floating user ID box with a copy button
    session_id = st.session_state.get("user_id", "USER-123456")

    st.markdown(f"""
        <div class="floating-user-id">
            <span>🆔 </span>
            <span>{session_id}</span>
        </div>
    """, unsafe_allow_html=True)
