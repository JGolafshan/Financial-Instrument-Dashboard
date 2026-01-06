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


# ==========================================================
# SAMPLE PORTFOLIO SEED
# ==========================================================
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


def main():
    set_page_state("pages/tracker.py")

    # Header
    st.title("Portfolio Risk Dashboard")
    st.caption(
        "Monitor portfolio composition, quantify downside risk, "
        "and evaluate historical stress scenarios."
    )

    with st.container():
        a1, a2, a3, _ = st.columns([1.2, 1.2, 1.2, 6.6])
        a1.button("Save Portfolio")
        a2.button("Load Portfolio")
        a3.button("Export Report")

    st.divider()

    # Setting Panel
    st.subheader("Analysis Configuration")
    st.caption("Define parameters used across all risk calculations")

    c1, c2, c3 = st.columns([1, 1, 2])

    with c1:
        look_back_period = st.number_input(
            "Rolling Window (Days)",
            min_value=1,
            value=5
        )

    with c2:
        confidence_interval = st.number_input(
            "Confidence Level (%)",
            min_value=1,
            max_value=100,
            value=95
        )

    with c3:
        st.info(
            "Changes here immediately affect VaR, CVaR "
            "and stress-test outputs.",
            icon="ℹ️"
        )

    st.divider()

    #KPI Metrics
    st.subheader("Portfolio Risk Snapshot")

    k1, k2, k3, k4,k5,k6,k7,k8 = st.columns(8)

    k1.metric("Value at Risk (VaR)", "4.00%")
    k2.metric("Conditional VaR", "5.00%")
    k3.metric("Portfolio Beta", "1.12")
    k4.metric("Risk Status", "Moderate", delta="▲ Elevated", delta_color="inverse")
    k5.metric("Value at Risk (VaR)", "4.00%")
    k6.metric("Conditional VaR", "5.00%")
    k7.metric("Portfolio Beta", "1.12")
    k8.metric("Risk Status", "Moderate", delta="▲ Elevated", delta_color="inverse")

    st.caption("Metrics based on historical simulation")

    st.divider()

    # Porfolio
    portfolio = pd.DataFrame(test_data)

    left, right = st.columns([0.65, 0.35], gap="large")

    # ---------------- Portfolio Editor ----------------
    with left:
        st.markdown("### Portfolio Composition")
        st.caption("Edit asset weights, quantities, and inclusion status")

        portfolio_data = st.data_editor(
            portfolio,
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

    with right:
        st.markdown("### Risk Interpretation")

        st.info(
            """
            **How to read these metrics**
            - **VaR**: Expected worst loss under normal conditions  
            - **CVaR**: Average loss beyond the VaR threshold  
            - **Beta**: Sensitivity to market-wide shocks  
            """,
            icon="📘"
        )

    st.divider()


    st.subheader("Historical Stress Testing")
    st.caption("Evaluate downside behaviour under rolling historical returns")

    with st.spinner("Downloading historical price data…"):
        adj_close_df = pd.DataFrame()

        for _, ticker in portfolio_data.iterrows():
            if not ticker["enabled"]:
                continue

            symbol = ticker["asset_name"]
            start_date = ticker["entry_at"]

            data = yf.download(symbol, start=start_date, progress=False)
            adj_close_df[symbol] = data["Close"]

    adj_close_df = adj_close_df.dropna()

    log_returns = np.log(adj_close_df / adj_close_df.shift(1)).dropna()

    weights = (
        portfolio_data
        .set_index("asset_name")["weight"]
        .loc[adj_close_df.columns]
    )
    weights = weights / weights.sum()

    portfolio_value = 100
    historical_return = (log_returns * weights).sum(axis=1)

    days = look_back_period
    range_returns = historical_return.rolling(window=days).sum().dropna()

    VaR = -np.percentile(
        range_returns,
        100 - confidence_interval
    ) * portfolio_value


    st.error(
        f"📉 **{days}-Day Value at Risk:** {VaR:.2f}",
        icon="⚠️"
    )

    with st.expander("Return Distribution & Stress Path"):
        st.line_chart(range_returns)

if __name__ == "__main__":
    main()
