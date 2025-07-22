#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Date: 04/04/2024
    Author: Joshua David Golafshan
"""

import numpy as np
import plotly.graph_objects as go
from src.core.black_scholes_model import BlackScholesModel


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
            bs_temp = BlackScholesModel(
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
            hovertemplate='Spot Price: %{x}<br>Volatility: %{y}<br>Premium: %{z}<extra></extra>'
        )
    )
    fig_call.update_layout(
        title=dict(text="Call Option", x=0.5, y=0.86, xanchor="center"),  # Centered Title
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
            hovertemplate='Spot Price: %{x}<br>Volatility: %{y}<br>Premium: %{z}<extra></extra>'

        )
    )
    fig_put.update_layout(
        title=dict(text="Put Option", x=0.5, y=0.86, xanchor="center"),  # Centered Title
        xaxis_title="Spot Price",
        yaxis_title="Volatility",
    )

    return fig_call, fig_put


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

    # Add the historical data (if available) as the first trace
    historical_data = simulation_dataframe["Historical Data"]
    fig.add_trace(
        go.Scatter(x=simulation_dataframe.index, y=historical_data, mode='lines', name="Historical Data",
                   line=dict(color='rgb(255, 99, 71)', width=4))  # Tomato Red for better contrast
    )

    # Add the group of simulated data as a single trace
    fig.add_trace(
        go.Scatter(x=simulation_dataframe.index, y=historical_data, mode='lines', name="Simulations",
                   line=dict(width=2, color='rgba(0, 255, 255, 0.6)', dash='dot'),
                   legendgroup="Simulations", showlegend=True, opacity=0.7)
    )

    # Add each simulation as a trace within the "Simulations" group
    for col in simulation_dataframe.columns[1:]:  # Skip 'Historical Data' column
        fig.add_trace(
            go.Scatter(x=simulation_dataframe.index, y=simulation_dataframe[col], mode='lines', name=col,
                       line=dict(width=1.5, color='rgba(0, 255, 255, 0.6)', dash='dot'),
                       legendgroup="Simulations", showlegend=False, opacity=0.7)
        )

    # Add a shaded area for the confidence interval (95% interval)
    upper_bound = simulation_dataframe.iloc[:, 1:].quantile(0.95, axis=1)
    lower_bound = simulation_dataframe.iloc[:, 1:].quantile(0.05, axis=1)

    fig.add_trace(
        go.Scatter(x=simulation_dataframe.index, y=upper_bound, mode='lines', name='95% Confidence Upper Bound',
                   fill='tonexty', fillcolor='rgba(0, 255, 255, 0.1)', line=dict(width=0), showlegend=False)
    )

    fig.add_trace(
        go.Scatter(x=simulation_dataframe.index, y=lower_bound, mode='lines', name='95% Confidence Lower Bound',
                   fill='tonexty', fillcolor='rgba(0, 255, 255, 0.1)', line=dict(width=0), showlegend=False)
    )

    # Customize the layout
    fig.update_layout(
        title='Monte Carlo Simulations with Historical Data & Confidence Interval',
        xaxis=dict(title='Date', tickangle=45, showgrid=True, tickformat='%b %d, %Y', gridcolor='rgb(49,51,63)'),
        yaxis=dict(title='Price', showgrid=True, zeroline=False, gridcolor='rgb(49,51,63)'),
        template='plotly_white',
        showlegend=True,
        hovermode='closest',
        margin=dict(l=50, r=50, t=50, b=50),
        legend=dict(x=0.5, y=-0.1, traceorder='normal', orientation='h', bgcolor='rgba(255, 255, 255, 0.6)',
                    bordercolor="rgba(255, 255, 255, 0.3)", borderwidth=1, xanchor='center', yanchor='bottom'),
        hoverlabel=dict(bgcolor="white", font_size=14, font_family="Arial", font_color="black"),
        paper_bgcolor='rgb(14, 17, 23, 0)',
        plot_bgcolor='rgb(14, 17, 23, 0)',
    )
    return fig
