#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Date: 01/11/2026
    Author: Joshua David Golafshan
"""

from dataclasses import dataclass
from typing import Any, List, Optional
import streamlit as st
import pandas as pd

@dataclass
class QueryDataType:
    query_name: str
    query_type: Any
    query_init_value: Optional[Any] = None


class QueryHandler:
    def __init__(self, query_list: List[QueryDataType]):
        self.query_list = query_list

    def init_query_parameters(self):
        for query in self.query_list:
            # Check if URL query parameter exists
            url_value = st.query_params.get(query.query_name)
            if url_value is not None:
                # st.query_params always gives a list of strings
                current_value = self._convert_value(url_value, query.query_type, query.query_init_value)
            else:
                # Use existing session_state or fallback
                current_value = st.session_state.get(query.query_name, query.query_init_value)
                current_value = self._convert_value(current_value, query.query_type, query.query_init_value)

            # Save to session_state
            st.session_state[query.query_name] = current_value

    def sync_query_params(self):
        """
        Update st.query_params based on session_state values.
        Preserves type conversions for URL-safe strings.
        """
        for query in self.query_list:
            value = st.session_state.get(query.query_name)

            # Remove empty values
            if value in ("", None):
                st.query_params.pop(query.query_name, None)
                continue

            # Convert to string for URL based on type
            st.query_params[query.query_name] = self._value_to_url_str(value, query.query_type)

    def clear(self):
        """
        Reset session_state values to their defaults and clear URL
        """
        for query in self.query_list:
            st.session_state[query.query_name] = query.query_init_value
        st.query_params.clear()

    def _convert_value(self, value: Any, target_type: Any, fallback: Any):
        """Convert a value to the target type safely."""
        try:
            if value is None:
                return fallback
            if target_type == int:
                return int(value)
            elif target_type == float:
                return float(value)
            elif target_type == str:
                return str(value)
            elif target_type == bool:
                return bool(value)
            elif target_type == pd.Timestamp:
                if isinstance(value, pd.Timestamp):
                    return value
                return pd.to_datetime(value)
            else:
                return value
        except Exception:
            return fallback

    def _value_to_url_str(self, value: Any, value_type: Any) -> str:
        """Convert a value to a string for URL query params."""
        if value_type == pd.Timestamp:
            return value.strftime("%Y-%m-%d")
        elif value_type == bool:
            return "1" if value else "0"
        else:
            return str(value)
