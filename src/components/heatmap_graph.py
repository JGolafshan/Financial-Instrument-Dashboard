#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Date: 04/04/2024
    Author: Joshua David Golafshan
"""

import numpy as np
import plotly.graph_objects as go
from src.core.black_scholes_model import BlackScholes


def plot_heatmap(bs_model, spot_range, vol_range, strike):
    """
    Generates heatmaps for call and put option prices using Plotly.

    :param bs_model: An instance of the Black-Scholes model with predefined parameters.
    :param spot_range: Array of spot prices (x-axis).
    :param vol_range: Array of volatilities (y-axis).
    :param strike: The strike price for the option.

    :return: Plotly figures (fig_call, fig_put)
    """
    call_prices = np.zeros((len(vol_range), len(spot_range)))
    put_prices = np.zeros((len(vol_range), len(spot_range)))

    custom_colorscale = [
        [0.0, "red"],
        [1.0, "green"]
    ]

    # Compute prices across spot and volatility ranges
    for i, vol in enumerate(vol_range):
        for j, spot in enumerate(spot_range):
            bs_temp = BlackScholes(
                time_to_maturity=bs_model.time_to_maturity,
                strike=strike,
                current_price=spot,
                volatility=vol,
                interest_rate=bs_model.interest_rate
            )
            call_price, put_price = bs_temp.calculate_prices()
            call_prices[i, j] = call_price
            put_prices[i, j] = put_price

    # Create Call Option Heatmap
    fig_call = go.Figure(
        data=go.Heatmap(
            z=call_prices,
            x=np.round(spot_range, 2),
            y=np.round(vol_range, 2),
            colorscale=custom_colorscale,
            colorbar=dict(title="Call Price"),
        )
    )
    fig_call.update_layout(
        title=dict(text="Call Option", x=0.5, xanchor="center"),  # Centered Title
        xaxis_title="Spot Price",
        yaxis_title="Volatility",
    )

    # Create Put Option Heatmap
    fig_put = go.Figure(
        data=go.Heatmap(
            z=put_prices,
            x=np.round(spot_range, 2),
            y=np.round(vol_range, 2),
            colorscale=custom_colorscale,
            colorbar=dict(title="Put Price"),
        )
    )
    fig_put.update_layout(
        title=dict(text="Put Option", x=0.5, xanchor="center"),  # Centered Title
        xaxis_title="Spot Price",
        yaxis_title="Volatility",
    )

    return fig_call, fig_put
