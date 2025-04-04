#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Date: 04/04/2024
    Author: Joshua David Golafshan
"""

import numpy as np
import streamlit as st
from src import cookies
from src.black_scholes_model import BlackScholes
from src.components import sidebar
from src.heatmap_graph import plot_heatmap
from utils import utils
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
    cols = st.columns([0.2, 0.8])
    # HEADER SECTION
    with cols[0]:
        st.header(f"{yahoo_data['longName']}")
    with cols[1]:
        st.subheader(f"({yahoo_data['symbol']})")

    # TABS SECTION
    tab1, tab2, tab3 = st.tabs(["📈 Historical Chart", "🧮 Black-Scholes", "🎲 Monte Carlo"])

    # TAB 1: Historical Chart
    with tab1:
        if not stock_data.empty:
            st.subheader("📈 Historical Stock Price")

            # User can pick what to view

            st.line_chart(stock_data[["Close"]])

    # TAB 2: Black-Scholes
    with tab2:
        col1, col2 = st.columns(2, gap="medium")

        with col1:
            # You can add inputs or explanations here
            st.markdown("#### Option Pricing Parameters")

        # Compute Call and Put values
        bs_model = BlackScholes(time_to_maturity, strike, current_price, volatility, interest_rate)
        call_price, put_price = bs_model.calculate_prices()

        with col2:
            st.markdown("#### Computed Prices")
            st.markdown(f"""
                <div class="metric-container metric-call">
                    <div>
                        <div class="metric-label">CALL Value</div>
                        <div class="metric-value">${call_price:.2f}</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            st.markdown(f"""
                <div class="metric-container metric-put">
                    <div>
                        <div class="metric-label">PUT Value</div>
                        <div class="metric-value">${put_price:.2f}</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

        st.markdown("---")
        st.subheader("🎯 Options Price - Interactive Heatmap")
        st.info(
            "Explore how option prices fluctuate with varying **Spot Prices** and **Volatility** levels, keeping Strike Price constant."
        )

        with st.expander("⚙️ Heatmap Settings", expanded=True):
            c1, c2 = st.columns(2)
            with c1:
                vol_min = st.slider('Min Volatility', 0.01, 1.0, value=volatility * 0.5, step=0.01)
                spot_min = st.number_input('Min Spot Price', 0.01, value=current_price * 0.8, step=0.01)
            with c2:
                vol_max = st.slider('Max Volatility', 0.01, 1.0, value=volatility * 1.5, step=0.01)
                spot_max = st.number_input('Max Spot Price', 0.01, value=current_price * 1.2, step=0.01)

            spot_range = np.linspace(spot_min, spot_max, 10)
            vol_range = np.linspace(vol_min, vol_max, 10)

        st.markdown("### 🔥 Heatmap Visualization")
        heat_col1, heat_col2 = st.columns(2, gap="medium")

        fig_call, fig_put = plot_heatmap(bs_model, spot_range, vol_range, strike)

        with heat_col1:
            st.plotly_chart(fig_call, use_container_width=True, config={'displayModeBar': False})

        with heat_col2:
            st.plotly_chart(fig_put, use_container_width=True, config={'displayModeBar': False})
    with tab3:
        if not stock_data.empty:
            st.subheader("📈 Historicalsss Stock Price")

            # User can pick what to view

            st.line_chart(stock_data[["Close"]])


# PAGE FALLBACK
if instrument_code and instrument_code != "NONE":
    show_info()
else:
    st.switch_page("pages/search.py")
