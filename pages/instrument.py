#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Date: 04/04/2024
    Author: Joshua David Golafshan
"""
import random

import numpy as np
import pandas as pd
import streamlit as st
from src.heatmap_graph import plot_heatmap
from utils import utils
from src import cookies
from src.components import sidebar
from src.black_scholes_model import BlackScholes
from utils.utils import set_page_state

st.set_page_config(
    page_title="Overview",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)
# Load Default Data
st.markdown(utils.load_css("assets/css/styles.css"), unsafe_allow_html=True)

# Session Data
session_id = cookies.get_session_id()
set_page_state("pages/instrument.py")
instrument_code = st.session_state.get("code", "NONE")
st.query_params.code = instrument_code

# Load Components
search_query = sidebar.sidebar()
utils.user_component()

current_price = 40
strike = 45
time_to_maturity = 1
volatility = 0.2
interest_rate = 0.05


def show_info():
    instrument_yahoo = utils.yahoo_data(instrument_code)
    yahoo_data = instrument_yahoo.info
    stock_data = instrument_yahoo.history()
    # Create the layout using Streamlit's columns
    cols = st.columns([0.5, 0.25, 0.25], border=True)

    # First Column (Company Info Card)
    with cols[0]:
        with st.container(key="company-card"):
            st.markdown(
                f"""
                <div style="display: flex;">
                    <img src="https://picsum.photos/50/50" class="company-logo" alt="Company Logo" >
                    <div>
                        <div style="display: flex; align-items: center;">
                            <h4 class="company-name" style="margin-right: 10px;">{yahoo_data['longName']}</h4> 
                            <h4 class="company-name">{yahoo_data['symbol']}</h4>
                        </div>
                        <div><span class="label">{yahoo_data['sectorDisp']}: </span><span class="value">{yahoo_data["industryDisp"]}</span></div>
                        <div>
                            <img class="flag" src="https://picsum.photos/25/25" alt="Country Flag" style="margin-right: 5px;">
                            <span class="value">Country</span>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
    # Second Column (EOD Card)
    with cols[1]:
        st.metric("Price", "70 °F", "1.2 °F")

    with cols[2]:
        pass

    tab1, tab2, tab3 = st.tabs(["Overview", "BlackSchole Model", "Monty Carlo"])
    with tab1:
        st.write("Overview")
    with tab2:
        with st.expander("Settings"):
            vol_min = st.slider('Min Volatility for Heatmap', min_value=0.01, max_value=1.0, value=volatility * 0.5,
                                step=0.01)
            vol_max = st.slider('Max Volatility for Heatmap', min_value=0.01, max_value=1.0, value=volatility * 1.5,
                                step=0.01)
            spot_min = st.number_input('Min Spot Price', min_value=0.01, value=current_price * 0.8, step=0.01)
            spot_max = st.number_input('Max Spot Price', min_value=0.01, value=current_price * 1.2, step=0.01)
            spot_range = np.linspace(spot_min, spot_max, 10)
            vol_range = np.linspace(vol_min, vol_max, 10)

        input_data = {
            "Current Asset Price": [current_price],
            "Strike Price": [strike],
            "Time to Maturity (Years)": [time_to_maturity],
            "Volatility (σ)": [volatility],
            "Risk-Free Interest Rate": [interest_rate],
        }
        input_df = pd.DataFrame(input_data)
        st.table(input_df)

        # Calculate Call and Put values
        bs_model = BlackScholes(time_to_maturity, strike, current_price, volatility, interest_rate)
        call_price, put_price = bs_model.calculate_prices()

        # Display Call and Put Values in colored tables
        col1, col2 = st.columns([1, 1], gap="small")

        with col1:
            # Using the custom class for CALL value
            st.markdown(f"""
                <div class="metric-container metric-call">
                    <div>
                        <div class="metric-label">CALL Value</div>
                        <div class="metric-value">${call_price:.2f}</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

        with col2:
            # Using the custom class for PUT value
            st.markdown(f"""
                <div class="metric-container metric-put">
                    <div>
                        <div class="metric-label">PUT Value</div>
                        <div class="metric-value">${put_price:.2f}</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

        st.markdown("")
        st.title("Options Price - Interactive Heatmap")
        st.info(
            "Explore how option prices fluctuate with varying 'Spot Prices and Volatility' levels using interactive heatmap parameters, all while maintaining a constant 'Strike Price'.")

        # Interactive Sliders and Heatmaps for Call and Put Options
        col1, col2 = st.columns([1, 1], gap="small")
        fig_call, fig_put = plot_heatmap(bs_model, spot_range, vol_range, strike)

        with col1:
            st.subheader("Call Price Heatmap")
            st.plotly_chart(fig_call, use_container_width=True, config={'displayModeBar': False})

        with col2:
            st.subheader("Put Price Heatmap")
            st.plotly_chart(fig_put, use_container_width=True, config={'displayModeBar': False})


if instrument_code and instrument_code != "NONE":
    show_info()
else:
    st.switch_page("pages/search.py")
