#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Date: 04/04/2024
    Author: Joshua David Golafshan
    Description: all individual stock (ticker relate functions)
"""
import orjson
import numpy as np
import streamlit as st
from src.utils.utils import set_page_state, yahoo_data
from src.components.simple_components import option_metric
from src.core.black_scholes_model import BlackScholesModel
from src.core.monte_carlo_simulation import MonteCarloSimulation
from src.components.graphing_components import plot_option_heatmap, monte_carlo_chart, historical_chart

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


def display_instrument(stock_info):
    st.html(f"""
                <div style="display:flex; align-items: baseline;">
                    <div style="font-size:2.25rem">{stock_info["longName"]}</div> 
                    <div style="padding-left:1rem; font-size:2.25rem">({stock_info["symbol"]})</div>
                </div>
            """)


def calculate_stock_summary_statistics(stock_data):
    latest_price = stock_data.iloc[-1]["Close"]
    st.session_state["current_price"] = latest_price // 1
    previous_year_price = stock_data.iloc[252]["Close"] if len(stock_data) > 252 else stock_data.iloc[0]["Close"]
    price_diff = latest_price - previous_year_price
    percent_diff = (price_diff / previous_year_price)
    latest_close_price = stock_data.iloc[-1]["Close"]
    high_52w = stock_data["High"].tail(252).max()
    low_52w = stock_data["Low"].tail(252).min()

    return latest_close_price, price_diff, percent_diff, high_52w, low_52w


def display_summary_statistics(stock_data):
    latest_close_price, price_diff, percent_diff, high_52_w, low_52_w = calculate_stock_summary_statistics(stock_data)
    col2, col3, col4, col5 = st.columns([1, 1, 1, 1])

    with col2:
        st.metric("Close Price", f"${latest_close_price:.2f}")
    with col3:
        st.metric("Price Difference (YoY)", f"${price_diff:.2f}", f"{percent_diff:+.2f}%")
    with col4:
        st.metric("52-Week High", f"${high_52_w:.2f}")
    with col5:
        st.metric("52-Week Low", f"${low_52_w:.2f}")


@st.fragment(run_every=None)
def show_bs_model():
    st.markdown("#### Black Scholes Model")

    col1, col2 = st.columns([4, 6], gap="large")

    with col1:
        st.subheader("Parameters")

        input_column_1, input_column_2 = st.columns(2)

        current_price = input_column_1.number_input(label="Current Price", value=st.session_state.get("current_price"), key="bs_price")
        strike = input_column_2.number_input(label="Strike", value=st.session_state.get("bs_price")*1.05, key="bs_strike")
        volatility = input_column_1.number_input(label="Volatility", value=0.2, key="bs_volatility")
        interest_rate = input_column_2.number_input(label="Interest rate", value=0.05, key="bs_interest_rate")
        time_to_maturity = input_column_1.number_input(label="Time to maturity", value=1, key="bs_time_to_maturity")
        num_of_contracts = input_column_2.number_input(label="Number of Contracts", value=1, key="num_of_contracts")

        st.markdown("---")
        input_column_12, input_column_22 = st.columns(2)
        vol_min = input_column_12.number_input('Min Volatility', 0.01, 1.0, value=volatility * 0.5, step=0.01)
        vol_max = input_column_12.number_input('Max Volatility', 0.01, 1.0, value=volatility * 1.5, step=0.01)
        spot_min = input_column_22.number_input('Min Spot Price', 0.01, value=st.session_state.get("bs_strike") * 0.8, step=0.01)
        spot_max = input_column_22.number_input('Max Spot Price', 0.01, value=st.session_state.get("bs_strike") * 1.2, step=0.01)

    with col2:
        st.subheader("Output")

        bs_model = BlackScholesModel(time_to_maturity, strike, current_price, volatility, interest_rate)
        call_price, put_price = bs_model.calculate_prices()
        greeks = bs_model.calculate_greeks()

        if strike == current_price:
            st.info("Strike equals current price — no Call or Put valuation shown.")
            return

        is_call = strike > current_price
        option_type = greeks["call"] if is_call else greeks["put"]
        css_type = "metric-call" if is_call else "metric-put"
        option_type_name = "Call Value" if is_call else "Put Value"

        st.html(option_metric(
            css_style=css_type,
            option_type=option_type_name,
            option_price=call_price,
            option_delta=option_type["delta"],
            option_theta=option_type["theta"],
            option_rho=option_type["rho"],
            option_gamma=greeks["gamma"],
            option_vega=greeks["vega"]
        ))

        spot_range = np.linspace(spot_min, spot_max, 10)
        vol_range = np.linspace(vol_min, vol_max, 10)

        if is_call:
            option_fig = plot_option_heatmap(bs_model, num_of_contracts, spot_range, vol_range, True)
            st.plotly_chart(option_fig, use_container_width=True, config={'displayModeBar': False})
        else:
            option_fig = plot_option_heatmap(bs_model, num_of_contracts, spot_range, vol_range, False)
            st.plotly_chart(option_fig, use_container_width=True, config={'displayModeBar': False})


def plot_historical_chart(stock_data):
    st.plotly_chart(historical_chart(stock_data), use_container_width=True)


@st.fragment(run_every=None)
def show_monte_carlo_page():
    st.subheader("📈 Monte Carlo Simulation ")

    with st.expander("⚙️ Settings", expanded=False):
        number_of_simulations = st.number_input('Number of Simulations', min_value=1, value=30, step=10, max_value=300)
        look_back = st.number_input('Look Back Period', min_value=1, value=30, step=5, max_value=100)
        look_forward = st.number_input('Look Forward Period', min_value=1, value=30, step=30, max_value=365 * 3)

    mc_sim = MonteCarloSimulation(get_instrument_data(instrument_code)["history"]["Close"], look_forward, look_back,
                                  number_of_simulations)
    mc_sim.simulate()
    simulation_results = mc_sim.get_simulation_results()
    st.plotly_chart(monte_carlo_chart(simulation_results), use_container_width=True)


def show_info(instrument_data):
    stock_info = instrument_data["info"]
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


if __name__ == "__main__":
    if instrument_code and instrument_code != "NONE":
        instrument_data = get_instrument_data(instrument_code)
        if instrument_data["info"]["trailingPegRatio"] is None:  # TODO this should be improved
            st.session_state["search_warning"] = f"Instrument {instrument_code} not found."
            st.switch_page("pages/search.py")
        else:
            show_info(instrument_data)
    else:
        st.switch_page("pages/search.py")
