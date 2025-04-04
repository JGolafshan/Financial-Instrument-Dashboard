#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Date: 04/04/2024
    Author: Joshua David Golafshan
"""

import streamlit as st
import uuid


def get_session_id():
    # Check if the cookie already exists
    if 'session_id' in st.session_state:
        return st.session_state['session_id']

    # If no session ID exists, generate a new one
    session_id = str(uuid.uuid4())  # Unique ID
    st.session_state['session_id'] = session_id  # Store it in the session state
    return session_id
