#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Date: 04/04/2024
Author: Joshua David Golafshan
Description: Portfolio risk & performance dashboard
"""

import base64
import pickle
import datetime
import numpy as np
import pandas as pd
import yfinance as yf
import streamlit as st
from typing import Dict
from src.utils.utils import set_page_state


FILTER_KEYS = ["period", "ci", "portfolio"]

def sync_query_params():
    for key in FILTER_KEYS:
        value = st.session_state.get(key)

        if key == "period" or key == "ci":
            st.query_params[key] = int(value)
            continue

        if value:
            st.query_params[key] = value

def dict_to_base64(d: Dict) -> str:
    return base64.urlsafe_b64encode(pickle.dumps(d)).decode("utf-8")


def base64_to_dict(s: str) -> Dict:
    return pickle.loads(base64.urlsafe_b64decode(s.encode("utf-8")))

DEFAULT_PORTFOLIO = {
    "AAPL": {
        "weight": 50,
        "entry_at": "2023-01-01",
        "enabled": True,
        "remove": False,
    },
    "MSFT": {
        "weight": 50,
        "entry_at": "2023-01-01",
        "enabled": True,
        "remove": False,
    },
}

def main():
    set_page_state()
    qp = st.query_params

    try:
        portfolio_dict = (
            base64_to_dict(qp["portfolio"])
            if "portfolio" in qp
            else DEFAULT_PORTFOLIO.copy()
        )
    except Exception:
        portfolio_dict = DEFAULT_PORTFOLIO.copy()

    look_back_period = int(qp.get("period", 5))
    confidence_interval = int(qp.get("ci", 95))

    st.title("Portfolio Risk Dashboard")
    st.caption("Monitor portfolio composition, quantify downside risk, and evaluate historical stress scenarios.")

    st.divider()
    st.subheader("Portfolio Risk Snapshot")
    st.caption("Metrics based on historical simulation")

    k1, k2, k3, k4, k5 = st.columns(5)

    st.divider()
    st.subheader("Analysis Configuration")
    st.caption("Define parameters used across all risk calculations")

    c1, c2, _ = st.columns([1, 1, 3])
    look_back_period = c1.number_input(
        label="Rolling Window (Days)",
        min_value=1,
        key="period",
        value=look_back_period,
        on_change=sync_query_params
    )
    confidence_interval = c2.number_input(
        label="Confidence Level (%)",
        key="ci",
        min_value=1,
        max_value=100,
        value=confidence_interval,
        on_change=sync_query_params
    )

    st.divider()
    st.subheader("Portfolio Composition")
    st.caption("Edit asset weights, quantities, and inclusion status")

    portfolio_col1, portfolio_col2, _ = st.columns([1.4,1.4, 7.2])
    with portfolio_col1.popover("Add New Asset"):
        new_asset = st.text_input("Ticker", value="NVDA")
        new_weight = st.number_input("Weight (%)", min_value=0, max_value=100, value=10)
        new_entry = st.date_input("Entry Date", value=datetime.date.today())
        new_enabled = st.checkbox("Include", value=True)

        if st.button("Add Asset"):
            portfolio_dict[new_asset.upper()] = {
                "weight": new_weight,
                "entry_at": str(new_entry),
                "enabled": new_enabled,
                "remove": False,
            }
            st.success(f"{new_asset.upper()} added")
            st.rerun()

    # Dict → DataFrame
    portfolio_df = (
        pd.DataFrame.from_dict(portfolio_dict, orient="index")
        .reset_index()
        .rename(columns={"index": "asset_name"})
    )

    portfolio_df["entry_at"] = pd.to_datetime(portfolio_df["entry_at"]).dt.date

    # Portfolio editor
    edited_df = st.data_editor(
        portfolio_df,
        hide_index=True,
        width='stretch',
        num_rows="dynamic",
        column_config={
            "remove": st.column_config.CheckboxColumn("Remove"),
            "asset_name": st.column_config.TextColumn("Asset"),
            "weight": st.column_config.NumberColumn("Weight (%)", min_value=0, max_value=100),
            "entry_at": st.column_config.DateColumn("Entry Date"),
            "enabled": st.column_config.CheckboxColumn("Include"),
        },
    )

    if portfolio_col2.button("Remove Selected Assets"):
        edited_df = edited_df[~edited_df["remove"]].drop(columns=["remove"])
        st.rerun()

    # DataFrame → dict
    portfolio_dict = (
        edited_df
        .assign(entry_at=lambda df: df["entry_at"].astype(str))
        .set_index("asset_name")
        .to_dict(orient="index")
    )

    # Download historical data (auto refreshes)
    @st.cache_data(show_spinner="Downloading historical prices…")
    def download_prices(portfolio: Dict):
        prices = pd.DataFrame()
        for asset, meta in portfolio.items():
            if not meta["enabled"]:
                continue
            data = yf.download(asset, start=meta["entry_at"], progress=False)
            prices[asset] = data["Close"]
        return prices.dropna()

    prices = download_prices(portfolio_dict)

    enabled_assets = [a for a, m in portfolio_dict.items() if m["enabled"]]
    prices = prices[enabled_assets]

    # Risk calculations
    log_returns = np.log(prices / prices.shift(1)).dropna()

    weights = pd.Series({a: portfolio_dict[a]["weight"] for a in enabled_assets})
    weights /= weights.sum()

    portfolio_returns = (log_returns * weights).sum(axis=1)

    rolling_returns = portfolio_returns.rolling(look_back_period).sum().dropna()
    losses = -rolling_returns

    VaR = np.percentile(losses, confidence_interval) * 100
    CVaR = losses[losses >= np.percentile(losses, confidence_interval)].mean() * 100

    cum_returns = (1 + portfolio_returns).cumprod()
    drawdown = cum_returns / cum_returns.cummax() - 1
    max_dd = drawdown.min()

    ann_return = portfolio_returns.mean() * 252
    ann_vol = portfolio_returns.std() * np.sqrt(252)

    # KPIs
    k1.metric("VaR", f"{VaR:.2f}%")
    k2.metric("CVaR", f"{CVaR:.2f}%")
    k3.metric("Max Drawdown", f"{-max_dd * 100:.2f}%")
    k4.metric("Annualized Return", f"{ann_return * 100:.2f}%")
    k5.metric("Annualized Volatility", f"{ann_vol * 100:.2f}%")

    # Chart
    with st.expander("Return Distribution & Stress Path", expanded=True):
        st.line_chart(rolling_returns)


if __name__ == "__main__":
    main()
