#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Date: 04/04/2024
Author: Joshua David Golafshan
Description: Portfolio risk & performance dashboard
"""

import datetime
import numpy as np
import pandas as pd
import yfinance as yf
import streamlit as st
from src.utils.utils import set_page_state


# Sample Portfolio Seed data
test_data = [
    {
        "asset_name": "TSLA",
        "weight": 10,
        "amount": 200,
        "entry_at": datetime.date.today() - datetime.timedelta(days=365 * 2),
        "enabled": True
    },
    {
        "asset_name": "AAPL",
        "weight": 90,
        "amount": 200,
        "entry_at": datetime.date.today() - datetime.timedelta(days=365 * 2),
        "enabled": True
    }
]


FILTER_KEYS = ["period", "ci", "portfolio"]

def sync_query_params():
    for key in FILTER_KEYS:
        value = st.session_state.get(key, None)
        if value:
            st.query_params[key] = value
        elif key in st.query_params:
            del st.query_params[key]


@st.cache_data(show_spinner="Downloading historical price data...")
def download_historical_portfolio(portfolio_data):
    adj_close_df = pd.DataFrame()
    for _, ticker in portfolio_data.iterrows():
        if not ticker["enabled"]:
            continue

        symbol = ticker["asset_name"]
        start_date = ticker["entry_at"]

        data = yf.download(symbol, start=start_date, progress=False)
        adj_close_df[symbol] = data["Close"]

    adj_close_df = adj_close_df.dropna()
    return adj_close_df



def main():
    set_page_state("pages/tracker.py")

    # Query params
    qp = st.query_params
    period_input = int(qp.get("period", 5))
    ci_input = int(qp.get("ci", 95))
    portfolio_data = qp.get("portfolio", "")

    # Header
    st.title("Portfolio Risk Dashboard")
    st.caption("Monitor portfolio composition, quantify downside risk, and evaluate historical stress scenarios.")

    with st.container():
        a1, a2, _ = st.columns([1.2, 1.2, 7.8])
        a1.button("Save Portfolio")
        a2.button("Load Portfolio")

    st.divider()

    # Setting Panel
    st.subheader("Analysis Configuration")
    st.caption("Define parameters used across all risk calculations")

    c1, c2, c3 = st.columns([1, 1, 2])

    with c1:
        look_back_period = st.number_input(
            "Rolling Window (Days)",
            min_value=1,
            value=period_input,
            key="period",
            on_change = sync_query_params
        )

    with c2:
        confidence_interval = st.number_input(
            "Confidence Level (%)",
            min_value=1,
            max_value=100,
            value=ci_input,
            key="ci",
            on_change=sync_query_params
        )


    st.divider()

    #KPI Metrics
    st.subheader("Portfolio Risk Snapshot")
    k1, k2, k3, k4,k5,k6,k7 = st.columns(7)

    st.caption("Metrics based on historical simulation")
    st.divider()



    # ---------------- Portfolio Editor ----------------
    with st.container(border=False):
        st.markdown("### Portfolio Composition")
        st.caption("Edit asset weights, quantities, and inclusion status")

        # Button to open modal
        with st.popover("Add New Asset"):
            # Default values
            new_asset_name = st.text_input("Asset Ticker", value="AAPL")
            new_weight = st.number_input("Weight (%)", min_value=0, max_value=100, value=10)
            new_amount = st.number_input("Quantity", min_value=1, value=100)
            new_entry_at = st.date_input("Entry Date", value=datetime.date.today())
            new_enabled = st.checkbox("Include in portfolio", value=True)

            if st.button("Add to Portfolio"):
                # Create a new row
                new_row = {
                    "asset_name": new_asset_name,
                    "weight": new_weight,
                    "amount": new_amount,
                    "entry_at": new_entry_at,
                    "enabled": new_enabled
                }

                # Append to current portfolio_data
                test_data.append(new_row)

                st.success(f"Added {new_asset_name} to portfolio!")

        # Portfolio
        portfolio = pd.DataFrame(test_data)
        portfolio_data = st.data_editor(
            data=portfolio,
            hide_index=True,
            use_container_width=True,
            column_config={
                "asset_name": st.column_config.TextColumn("Asset"),
                "weight": st.column_config.NumberColumn(
                    "Weight (%)", format="%d%%", min_value=0, max_value=100
                ),
                "amount": st.column_config.NumberColumn("Quantity"),
                "entry_at": st.column_config.DateColumn("Entry Date"),
                "enabled": st.column_config.CheckboxColumn("Include"),
            }
        )

        total_weight = portfolio_data["weight"].sum()
        if total_weight != 100:
            st.warning(f"Total portfolio weight is {total_weight}%, not 100%.")

    st.divider()

    st.subheader("Historical Stress Testing")
    st.caption("Evaluate downside behaviour under rolling historical returns")


    adj_close_df = download_historical_portfolio(portfolio_data=portfolio)



    adj_close_updated = adj_close_df.loc[:, portfolio_data.loc[portfolio_data["enabled"], "asset_name"]]

    log_returns = np.log(adj_close_updated / adj_close_updated.shift(1)).dropna()

    weights = (portfolio_data.set_index("asset_name")["weight"].loc[adj_close_updated.columns])
    weights = weights / weights.sum()

    portfolio_value = 100
    historical_return = (log_returns * weights).sum(axis=1)

    days = look_back_period
    range_returns = historical_return.rolling(window=days).sum().dropna()

    losses = -range_returns

    # VaR (loss quantile)
    VaR = np.percentile(losses, confidence_interval) * portfolio_value

    # CVaR (Expected Shortfall)
    CVaR = losses[losses >= VaR / portfolio_value].mean() * portfolio_value

    #Maximum drawdown
    cum_returns = (1 + historical_return).cumprod()
    drawdown = cum_returns / cum_returns.cummax() - 1
    max_dd = drawdown.min()

    # Annualized return
    ann_return = historical_return.mean() * 252
    ann_vol = historical_return.std() * np.sqrt(252)

    k1.metric("Value at Risk (VaR)", f"{-VaR:.2f}%")
    k2.metric("Conditional VaR",  f"{-CVaR:.2f}%")
    k3.metric("Maximum Drawdown", f"{int(-max_dd*100)}%")
    k4.metric("Annualized Return", f"{int(ann_return*100)}%")
    k5.metric("Annualized Vol.", f"{int(ann_vol*100)}%")


    with st.expander("Return Distribution & Stress Path", True):
        st.line_chart(range_returns)

if __name__ == "__main__":
    main()
