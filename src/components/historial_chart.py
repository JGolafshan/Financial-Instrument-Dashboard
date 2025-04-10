#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Date: 10/04/2024
    Author: Joshua David Golafshan
"""

import plotly.graph_objs as go


def historical_chart(stock_history):
    candlestick_chart = go.Figure(data=[
        go.Candlestick(x=stock_history.index, open=stock_history['Open'], high=stock_history['High'],
                       low=stock_history['Low'], close=stock_history['Close'])])
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

    return candlestick_chart
