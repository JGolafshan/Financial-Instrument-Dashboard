#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Date: 04/04/2024
    Author: Joshua David Golafshan
    Description: all individual stock (ticker relate functions)
"""
import pprint
import time
import orjson
import datetime
import numpy as np
import streamlit as st
from zoneinfo import ZoneInfo
import plotly.graph_objs as go
from src.utils.utils import set_page_state, yahoo_data
from streamlit_javascript import st_javascript
from src.components.custom_metric import option_metric
from src.components.heatmap_graph import plot_heatmap
from src.core.black_scholes_model import BlackScholesModel
from src.core.monte_carlo_simulation import MonteCarloSimulation

# Load Components
set_page_state("pages/instrument.py")
instrument_code = st.session_state.get("code", "NONE")
st.query_params.code = instrument_code


@st.cache_data(show_spinner="Fetching instrument data...")
def get_instrument_data(symbol: str):
    ticker = yahoo_data(symbol)
    return {
        "info": ticker.info,
        "history": ticker.history(period="max")
    }


@st.cache_data(show_spinner="Loading market data...")
def load_market_data(symbol: str):
    """Load and clean market data from JSON file."""
    with open("static/market_data.json") as f:
        data = orjson.loads(f.read())
        return data[symbol]


def calculate_user_time():
    timezone = st_javascript("""await (async () => {
                const userTimezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
                console.log(userTimezone)
                return userTimezone
    })().then(returnValue => returnValue)""", "casdsdslulate_user_time")
    user_timedate = datetime.datetime.now(tz=ZoneInfo(timezone))
    return user_timedate


def calculate_market_time(exchange_data: dict):
    pass


def market__status():
    pass


def market_status(is_market_open: bool):
    if is_market_open:
        return st.metric("Market closes in", f"{'~6 Hours'}")
    return st.metric("Market opens in ", f"{'~12 Hours'}")


def instrument_change(is_market_open: bool):
    if is_market_open:
        return st.metric("Current Price", f"${178.42}", f"{1.03:+.2f}%")
    return st.metric("Previous Day Change", f"${178.42}", f"{1.03:+.2f}%")


def display_instrument(stock_info):
    st.html(f"""
                <div style="display:flex; align-items: baseline;">
                    <div style="font-size:2.25rem">{stock_info["longName"]}</div> 
                    <div style="padding-left:1rem; font-size:2.25rem">({stock_info["symbol"]})</div>
                </div>
            """)


def calculate_stock_summary_statistics(stock_data):
    latest_price = stock_data.iloc[-1]["Close"]
    previous_year_price = stock_data.iloc[-252]["Close"] if len(stock_data) > 252 else stock_data.iloc[0]["Close"]
    price_diff = latest_price - previous_year_price
    pct_diff = (price_diff / previous_year_price) * 100
    latest_close_price = stock_data.iloc[-1]["Close"]
    high_52w = stock_data["High"].tail(252).max()
    low_52w = stock_data["Low"].tail(252).min()

    return price_diff, pct_diff, latest_close_price, high_52w, low_52w


def display_summary_statistics(stock_data):
    latest_close_price, prc_diff, pct_diff, high_52_w, low_52_w = calculate_stock_summary_statistics(stock_data)
    col0, col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 1, 1])

    with col0:
        instrument_change(False)
    with col1:
        market_status(True)
    with col2:
        st.metric("Close Price", f"${latest_close_price:.2f}")
    with col3:
        st.metric("Price Difference (YoY)", f"${prc_diff:.2f}", f"{pct_diff:+.2f}%")
    with col4:
        st.metric("52-Week High", f"${high_52_w:.2f}")
    with col5:
        st.metric("52-Week Low", f"${low_52_w:.2f}")


def show_bs_model():
    col1, col2 = st.columns(2, gap="medium")
    with col1:
        st.markdown("#### Option Pricing Parameters")
        input_column_1, input_column_2 = st.columns(2)

        current_price = input_column_1.number_input(label="Current Price",
                                                    value=st.session_state.get("bs_current_price", 40),
                                                    key="bs_current_price")
        strike = input_column_1.number_input(label="Strike", value=45, key="bs_strike")
        volatility = input_column_2.number_input(label="Volatility", value=0.2, key="bs_volatility")
        interest_rate = input_column_2.number_input(label="Interest rate", value=0.05, key="bs_interest_rate")
        time_to_maturity = st.number_input(label="Time to maturity", value=1, key="bs_time_to_maturity")

    bs_model = BlackScholesModel(time_to_maturity, strike, current_price, volatility, interest_rate)
    call_price, put_price = bs_model.calculate_prices()
    greeks = bs_model.calculate_greeks()

    with col2:
        st.markdown(f"#### Computed Prices: Gamma={greeks["gamma"]:.2f}, Vega={greeks["vega"]:.2f}")
        st.html(option_metric(css_style="metric-call", option_type="Call Value", option_price=call_price,
                              option_delta=greeks["call_delta"], option_theta=greeks["call_theta"],
                              option_rho=greeks["call_rho"]))
        st.html(option_metric(css_style="metric-put", option_type="Put Value", option_price=put_price,
                              option_delta=greeks["put_delta"], option_theta=greeks["put_theta"],
                              option_rho=greeks["put_rho"]))

    st.markdown("---")
    st.subheader("🎯 Options Price - Interactive Heatmap")

    with st.expander("⚙️ Heatmap Settings", expanded=False):
        c1, c2 = st.columns(2)
        vol_min = c1.slider('Min Volatility', 0.01, 1.0, value=volatility * 0.5, step=0.01)
        vol_max = c1.slider('Max Volatility', 0.01, 1.0, value=volatility * 1.5, step=0.01)
        spot_min = c2.number_input('Min Spot Price', 0.01, value=current_price * 0.8, step=0.01)
        spot_max = c2.number_input('Max Spot Price', 0.01, value=current_price * 1.2, step=0.01)

        # Generate this in function
        spot_range = np.linspace(spot_min, spot_max, 10)
        vol_range = np.linspace(vol_min, vol_max, 10)

    fig_call, fig_put = plot_heatmap(bs_model, spot_range, vol_range, strike)
    heat_col1, heat_col2 = st.columns(2, gap="medium")
    heat_col1.plotly_chart(fig_call, use_container_width=True, config={'displayModeBar': False})
    heat_col2.plotly_chart(fig_put, use_container_width=True, config={'displayModeBar': False})


def plot_historical_chart(stock_data):
    # TODO: Make this into .py
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


def show_monte_carlo_page():
    st.subheader("📈 Monte Carlo Simulation ")
    with st.expander("⚙️ Settings", expanded=False):
        number_of_simulations = st.number_input('Number of Simulations', min_value=1, value=30, step=5)
        look_back = st.number_input('Look Back Period', min_value=1, value=30, step=5)
        look_forward = st.number_input('Look Forward Period', 1, value=30, step=5)

    mc_sim = MonteCarloSimulation(get_instrument_data(instrument_code)["history"], look_forward, number_of_simulations)
    mc_sim.simulate()
    st.line_chart(mc_sim.get_simulation_results())


def show_info():
    instrument_data = get_instrument_data(instrument_code)
    if instrument_data is None:
        st.warning(f"Instrument {instrument_code} not found.")
        return

    stock_info = instrument_data["info"]
    pprint.pprint(stock_info)
    stock_data = instrument_data["history"]

    display_instrument(stock_info)
    display_summary_statistics(stock_data)

    # Use distinct tab names
    chart_tab, bs_model_tab, monte_carlo_tab = st.tabs(["📈 Historical Chart", "🧮 Black-Scholes", "🎲 Monte Carlo"])

    with chart_tab:
        if not stock_data.empty:
            plot_historical_chart(stock_data)

    with bs_model_tab:
        show_bs_model()

    with monte_carlo_tab:
        show_monte_carlo_page()


if instrument_code and instrument_code != "NONE":
    show_info()
else:
    st.switch_page("pages/search.py")
