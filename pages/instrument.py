#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Date: 04/04/2024
    Author: Joshua David Golafshan
    Description: all individual stock (ticker relate functions)
"""

import numpy as np
import streamlit as st
from src.utils import utils
from src.utils.utils import set_page_state
import plotly.graph_objs as go
from src.components.heatmap_graph import plot_heatmap
from src.core.black_scholes_model import BlackScholes

# Load Components
set_page_state(f"pages/{__name__}")
instrument_code = st.session_state.get("code", "NONE")
st.query_params.code = instrument_code


def calculate_price_difference(stock_data):
    latest_price = stock_data.iloc[-1]["Close"]
    previous_year_price = stock_data.iloc[-252]["Close"] if len(stock_data) > 252 else stock_data.iloc[0]["Close"]
    price_difference = latest_price - previous_year_price
    percentage_difference = (price_difference / previous_year_price) * 100
    return price_difference, percentage_difference


def show_header(**kwargs):
    pass


def show_graph():
    pass


def market_open():
    pass
    # Change 5 min
    # Change 30 min
    # Change 60 min

    # Time til close
    # Market closed in x


def market_closed():
    pass
    # Time till open
    # Location
    #


def show_info():
    instrument_yahoo = utils.yahoo_data(instrument_code)

    if instrument_yahoo:
        stock_data = instrument_yahoo.history()

        if stock_data is not None:
            price_difference, percentage_difference = calculate_price_difference(stock_data)
            latest_close_price = stock_data.iloc[-1]["Close"]
            max_52_week_high = stock_data["High"].tail(252).max()
            min_52_week_low = stock_data["Low"].tail(252).min()

        col0, col1, col2, col3, col4 = st.columns([0.2, 0.15, 0.15, 0.15, 0.15], )
        with col0:
            st.metric("Close Price", f"${latest_close_price:.2f}")
        with col1:
            st.metric("Close Price", f"${latest_close_price:.2f}")
        with col2:
            st.metric("Price Difference (YoY)", f"${price_difference:.2f}", f"{percentage_difference:+.2f}%")
        with col3:
            st.metric("52-Week High", f"${max_52_week_high:.2f}")
        with col4:
            st.metric("52-Week Low", f"${min_52_week_low:.2f}")

    # TABS SECTION
    tab1, tab2, tab3 = st.tabs(["📈 Historical Chart", "🧮 Black-Scholes", "🎲 Monte Carlo"])

    # TAB 1: Historical Chart
    with tab1:
        if not stock_data.empty:
            # User can pick what to view
            candlestick_chart = go.Figure(data=[
                go.Candlestick(x=stock_data.index, open=stock_data['Open'], high=stock_data['High'],
                               low=stock_data['Low'], close=stock_data['Close'])])
            candlestick_chart.update_xaxes(
                rangeslider_visible=True,
                rangeselector=dict(
                    buttons=list([
                        dict(count=1, label="1m", step="month", stepmode="backward"),
                        dict(count=6, label="6m", step="month", stepmode="backward"),
                        dict(count=1, label="YTD", step="year", stepmode="todate"),
                        dict(count=1, label="1y", step="year", stepmode="backward"),
                        dict(step="all")
                    ])
                )
            )
            candlestick_chart.update_layout(xaxis_rangeslider_visible=False)
            st.plotly_chart(candlestick_chart, use_container_width=True)

    # TAB 2: Black-Scholes
    with tab2:
        col1, col2,col3 = st.columns(3, gap="medium")

        with col1:
            # You can add inputs or explanations here
            st.markdown("#### Option Pricing Parameters")
            input_columns = st.columns(2)

            with input_columns[0]:
                current_price = st.number_input(label="Current Price", value=st.session_state.get("bs_current_price", 40), key="bs_current_price")

                strike = st.number_input(label="Strike", value=45, key="bs_strike")

            with input_columns[1]:
                volatility = st.number_input(label="Volatility", value=0.2, key="bs_volatility")
                interest_rate = st.number_input(label="Interest rate", value=0.05, key="bs_interest_rate")

            time_to_maturity = st.number_input(label="Time to maturity", value=1, key="bs_time_to_maturity")



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

        with col3:
            bs_model = BlackScholes(time_to_maturity, strike, current_price, volatility, interest_rate)
            greeks = bs_model.calculate_greeks()
            st.write(greeks)

        st.markdown("---")
        st.subheader("🎯 Options Price - Interactive Heatmap")

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
