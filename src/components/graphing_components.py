#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Date: 04/04/2024
    Author: Joshua David Golafshan
"""

import numpy as np
import plotly.graph_objects as go

from src.core.black_scholes_model import BlackScholesModel


def plot_option_heatmap(bs_model, num_of_contract, spot_range, vol_range, is_call=True):
    """
    Generates a heatmap for option prices (call or put) based on varying spot and vol.

    :param bs_model: A Black-Scholes model with base parameters (used for T, r, strike).
    :param spot_range: 1D array of spot prices (x-axis).
    :param vol_range: 1D array of volatilities (y-axis).
    :param is_call: Whether to compute call (True) or put (False) prices.
    :return: Plotly heatmap figure.
    """
    premiums = np.zeros((len(vol_range), len(spot_range)))
    profits = np.zeros((len(vol_range), len(spot_range)))

    for i, vol in enumerate(vol_range):
        for j, spot in enumerate(spot_range):
            temp_model = BlackScholesModel(
                time_to_maturity=bs_model.time_to_maturity,
                strike=bs_model.strike,
                current_price=spot,
                volatility=vol,
                interest_rate=bs_model.interest_rate
            )
            call_price, put_price = temp_model.calculate_prices()
            premium = call_price if is_call else put_price
            premiums[i, j] = premium

            if is_call:
                profits[i, j] = ((spot - bs_model.strike) * 100 * num_of_contract) - (premium * 100 * num_of_contract)

            else:
                profits[i, j] = ((bs_model.strike - spot) * 100 * num_of_contract) - (premium * 100 * num_of_contract)

    fig = go.Figure(data=go.Heatmap(
        z=premiums,
        x=np.round(spot_range, 2),
        y=np.round(vol_range, 2),
        colorscale=[[0.0, "red"], [1.0, "green"]],
        colorbar=dict(title="Premium"),
        customdata=np.expand_dims(profits, axis=-1),
        hovertemplate=(
            'Spot: %{x:.2f}<br>'
            'Vol: %{y:.2f}<br>'
            'Premium: %{z:.2f}<br>'
            # 'Profit: %{customdata:.2f}<extra></extra>'
        )
    ))

    fig.update_layout(
        title=dict(
            text=f"{'Call' if is_call else 'Put'} Option Premium Heatmap",
            x=0.5,
            y=0.86,
            xanchor="center"
        ),
        xaxis_title="Spot Price",
        yaxis_title="Volatility",
    )

    return fig


def historical_chart(stock_history):
    x = stock_history.index
    y = stock_history["Close"]

    fig = go.Figure()

    # Area under line with alpha
    fig.add_trace(go.Scatter(
        x=x,
        y=y,
        mode="lines",
        name="Close Price",
        line=dict(color="rgba(0, 128, 255, 1)", width=2),
        fill="tozeroy",
        fillcolor="rgba(0, 128, 255, 0.2)",  # semi-transparent fade
        hovertemplate="Date: %{x}<br>Price: %{y:$,.2f}<extra></extra>"
    ))

    # Range selector
    fig.update_xaxes(
        rangeselector=dict(
            buttons=list([
                dict(count=1, label="1m", step="month", stepmode="backward"),
                dict(count=6, label="6m", step="month", stepmode="backward"),
                dict(count=1, label="YTD", step="year", stepmode="todate"),
                dict(count=1, label="1y", step="year", stepmode="backward"),
                dict(step="all", label="All")
            ])
        ),
        rangeslider_visible=False,
        title="Date"
    )

    # Y-axis auto-range
    fig.update_yaxes(
        autorange=True,
        fixedrange=False,
        title="Price (USD)"
    )

    # Layout styling
    fig.update_layout(
        template="plotly_white",
        hovermode="x unified",
        margin=dict(t=20, l=0, r=0, b=0),
        height=500,
        showlegend=False
    )

    return fig


def monte_carlo_chart(simulation_dataframe):
    fig = go.Figure()

    # Add historical data
    fig.add_trace(
        go.Scatter(
            x=simulation_dataframe.index,
            y=simulation_dataframe["Historical Data"],
            mode='lines',
            name="Historical Data",
            line=dict(color='navy', width=3)
        )
    )

    # Confidence interval bounds (95%)
    upper_bound = simulation_dataframe.iloc[:, 1:].quantile(0.95, axis=1)
    lower_bound = simulation_dataframe.iloc[:, 1:].quantile(0.05, axis=1)

    fig.add_trace(
        go.Scatter(
            x=simulation_dataframe.index,
            y=upper_bound,
            mode='lines',
            line=dict(width=0),
            name='Upper Bound',
            showlegend=False
        )
    )

    fig.add_trace(
        go.Scatter(
            x=simulation_dataframe.index,
            y=lower_bound,
            mode='lines',
            fill='tonexty',
            fillcolor='rgba(173, 216, 230, 0.3)',  # light blue
            line=dict(width=0),
            name='Confidence Interval',
            showlegend=True
        )
    )

    # One representative simulation (legend-enabled)
    sample_sim = simulation_dataframe.columns[1]
    fig.add_trace(
        go.Scatter(
            x=simulation_dataframe.index,
            y=simulation_dataframe[sample_sim],
            mode='lines',
            name="Simulations",
            line=dict(width=1.5, color='rgba(100, 149, 237, 0.7)', dash='dot'),  # cornflower blue
            showlegend=True
        )
    )

    # Remaining simulations (legend disabled)
    for col in simulation_dataframe.columns[2:]:
        fig.add_trace(
            go.Scatter(
                x=simulation_dataframe.index,
                y=simulation_dataframe[col],
                mode='lines',
                name=col,
                line=dict(width=1.2, color='rgba(100, 149, 237, 0.25)', dash='dot'),
                showlegend=False
            )
        )

    # Layout customization
    fig.update_layout(
        title='Monte Carlo Simulations with Historical Data & 95% Confidence Interval',
        xaxis=dict(
            title='Date',
            tickangle=45,
            tickformat='%b %d, %Y',
            showgrid=True,
            gridcolor='rgba(200, 200, 200, 0.3)'
        ),
        yaxis=dict(
            title='Price',
            showgrid=True,
            gridcolor='rgba(200, 200, 200, 0.3)'
        ),
        template='plotly_white',
        showlegend=True,
        hovermode='x unified',
        margin=dict(l=40, r=40, t=60, b=50),
        legend=dict(
            orientation="h",
            x=0.5,
            y=-0.2,
            xanchor="center",
            yanchor="top",
            bgcolor='rgba(255, 255, 255, 0.8)',
            bordercolor="rgba(200, 200, 200, 0.5)",
            borderwidth=1
        ),
        hoverlabel=dict(
            bgcolor="white",
            font_size=13,
            font_family="Arial",
            font_color="black"
        ),
        paper_bgcolor='white',
        plot_bgcolor='white',
    )

    return fig

